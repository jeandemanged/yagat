#
# Copyright (c) 2024, Damien Jeandemange (https://github.com/jeandemanged)
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
# SPDX-License-Identifier: MPL-2.0
#
import logging
import tkinter as tk
from typing import Callable, Optional

import pypowsybl.network as pn
import pypowsybl.loadflow as lf

import yagat.networkstructure as ns


class AppContext:
    def __init__(self, root: tk.Tk):
        self._root = root
        self._network: Optional[pn.Network] = None
        self._lf_parameters: lf.Parameters = lf.Parameters()
        self._network_structure: Optional[ns.NetworkStructure] = None
        self._selection: tuple[Optional[str], Optional[str], Optional[ns.Connection]] = (None, None, None)
        self._status_text: str = 'Welcome'
        self._selected_tab: str = ''
        self._selected_view: str = ''
        self.status_text_changed_listeners = []
        self.network_changed_listeners = []
        self.selection_changed_listeners = []
        self.tab_changed_listeners = []
        self.view_changed_listeners = []

    @property
    def tk_root(self) -> tk.Tk:
        return self._root

    @property
    def status_text(self) -> str:
        return self._status_text

    @status_text.setter
    def status_text(self, value: str) -> None:
        logging.info(value)
        self._status_text = value
        self.notify_status_text_changed()

    @property
    def selected_tab(self) -> str:
        return self._selected_tab

    @selected_tab.setter
    def selected_tab(self, value: str) -> None:
        self._selected_tab = value
        self.notify_tab_changed()

    @property
    def selected_view(self) -> str:
        return self._selected_view

    @selected_view.setter
    def selected_view(self, value: str) -> None:
        self._selected_view = value
        self.notify_view_changed()

    @property
    def network(self) -> Optional[pn.Network]:
        return self._network

    @property
    def lf_parameters(self) -> lf.Parameters:
        return self._lf_parameters

    @property
    def network_structure(self) -> Optional[ns.NetworkStructure]:
        return self._network_structure

    @network.setter
    def network(self, new_network: Optional[pn.Network]) -> None:
        self._network = new_network
        if new_network:
            self._network_structure = ns.NetworkStructure(new_network)
        else:
            self._network_structure = None
        self.selection = (None, None, None)
        self.notify_network_changed()

    @property
    def selection(self) -> tuple[Optional[str], Optional[str], Optional[ns.Connection]]:
        return self._selection

    @selection.setter
    def selection(self, value: tuple[Optional[str], Optional[str], Optional[ns.Connection]]) -> None:
        logging.info(f'selection setter called {value[0]},{value[1]}')
        self._selection = value
        self.notify_selection_changed()

    def reset_selected_connection(self):
        self._selection = (self._selection[0], self._selection[1], None)

    def add_status_text_listener(self, listener: Callable[[str], None]) -> None:
        self.status_text_changed_listeners.append(listener)

    def notify_status_text_changed(self) -> None:
        for listener in self.status_text_changed_listeners:
            listener(self.status_text)

    def add_network_changed_listener(self, listener: Callable[[Optional[pn.Network]], None]) -> None:
        self.network_changed_listeners.append(listener)

    def notify_network_changed(self) -> None:
        for listener in self.network_changed_listeners:
            listener(self.network)

    def add_selection_changed_listener(self, listener: Callable[[tuple[Optional[str], Optional[str], Optional[ns.Connection]]], None]) -> None:
        self.selection_changed_listeners.append(listener)

    def notify_selection_changed(self) -> None:
        for listener in self.selection_changed_listeners:
            listener(self.selection)

    def add_tab_changed_listener(self, listener: Callable[[str], None]) -> None:
        self.tab_changed_listeners.append(listener)

    def notify_tab_changed(self) -> None:
        for listener in self.tab_changed_listeners:
            listener(self.selected_tab)

    def add_view_changed_listener(self, listener: Callable[[str], None]) -> None:
        self.view_changed_listeners.append(listener)

    def notify_view_changed(self) -> None:
        for listener in self.view_changed_listeners:
            listener(self.selected_view)
