#
# Copyright (c) 2024, Damien Jeandemange (https://github.com/jeandemanged)
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
# SPDX-License-Identifier: MPL-2.0
#
import tkinter as tk
from tkinter import filedialog as fd

import pypowsybl as pp
import pypowsybl.network as pn

from yagat.app_context import AppContext


class FileMenu(tk.Menu):
    def __init__(self, parent, context: AppContext, *args, **kwargs):
        tk.Menu.__init__(self, parent, *args, **kwargs)

        self.parent = parent
        self.context = context

        parent.add_cascade(
            label="File",
            menu=self,
            underline=0,
        )

        self.add_command(label='Open...', command=self.open_network)

        self.sample_networks_menu = tk.Menu(self)
        self.add_cascade(label='Open sample network', menu=self.sample_networks_menu)

        def load_sample_network(network: pn.Network):
            context.network = network
            context.status_text = 'Network ' + network.name + ' loaded'

        def load_be_nl():
            be = pn.create_micro_grid_be_network()
            be.merge(pn.create_micro_grid_nl_network())
            context.network = be
            context.status_text = 'Network CGMES MicroGrid BE+NL loaded'

        self.sample_networks_menu.add_command(label='IEEE 9 Bus',
                                              command=lambda: load_sample_network(pn.create_ieee9()))
        self.sample_networks_menu.add_command(label='IEEE 14 Bus',
                                              command=lambda: load_sample_network(pn.create_ieee14()))
        self.sample_networks_menu.add_command(label='IEEE 30 Bus',
                                              command=lambda: load_sample_network(pn.create_ieee30()))
        self.sample_networks_menu.add_command(label='IEEE 57 Bus',
                                              command=lambda: load_sample_network(pn.create_ieee57()))
        self.sample_networks_menu.add_command(label='IEEE 118 Bus',
                                              command=lambda: load_sample_network(pn.create_ieee118()))
        self.sample_networks_menu.add_command(label='IEEE 300 Bus',
                                              command=lambda: load_sample_network(pn.create_ieee300()))
        self.sample_networks_menu.add_command(label='CGMES MicroGrid BE',
                                              command=lambda: load_sample_network(pn.create_micro_grid_be_network()))
        self.sample_networks_menu.add_command(label='CGMES MicroGrid NL',
                                              command=lambda: load_sample_network(pn.create_micro_grid_nl_network()))
        self.sample_networks_menu.add_command(label='CGMES MicroGrid BE+NL',
                                              command=lambda: load_be_nl())
        self.sample_networks_menu.add_command(label='PowSyBl Metrix 6 Bus', command=lambda: load_sample_network(
            pn.create_metrix_tutorial_six_buses_network()))
        self.sample_networks_menu.add_command(label='Eurostag Tutorial', command=lambda: load_sample_network(
            pn.create_eurostag_tutorial_example1_network()))
        self.sample_networks_menu.add_command(label='Eurostag Tutorial with power limits',
                                              command=lambda: load_sample_network(
                                                  pn.create_eurostag_tutorial_example1_with_power_limits_network()))
        self.sample_networks_menu.add_command(label='Four Substations Node-Breaker',
                                              command=lambda: load_sample_network(
                                                  pn.create_four_substations_node_breaker_network()))
        self.sample_networks_menu.add_command(label='Four Substations Node-Breaker with extensions',
                                              command=lambda: load_sample_network(
                                                  pn.create_four_substations_node_breaker_network_with_extensions()))

        self.add_separator()
        self.add_command(label='Save...', command=self.save_network)
        self.add_separator()
        self.add_command(
            label='Exit',
            command=context.tk_root.destroy,
            underline=1,
        )

    def open_network(self):
        filename = fd.askopenfilename()
        if not filename:
            self.context.status_text = 'File opening cancelled by user'
        else:
            self.context.status_text = 'Opening ' + filename
            # disable the network changed listener, the tree view update is messed up in GUI if updated in thread
            self.context.network_changed_listener_enabled = False

            def task():
                self.context.network = pp.network.load(filename)

            def on_done():
                self.context.status_text = f'Network {self.context.network.name} loaded'
                self.context.network_changed_listener_enabled = True
                self.context.notify_network_changed()

            self.context.start_long_running_task(name='Opening file', target=task, on_done=on_done)

    def save_network(self):
        if not self.context.network:
            return
        filename = fd.asksaveasfilename()
        if not filename:
            self.context.status_text = 'File save cancelled by user'
        else:
            self.context.status_text = f'Saving {filename}'

            def on_done():
                self.context.status_text = f'Network {self.context.network.name} saved to {filename}'

            def task():
                self.context.network.save(filename)

            self.context.start_long_running_task(name='Saving file', target=task, on_done=on_done)
