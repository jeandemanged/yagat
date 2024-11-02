#
# Copyright (c) 2024, Damien Jeandemange (https://github.com/jeandemanged)
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
# SPDX-License-Identifier: MPL-2.0
#
import tkinter as tk

import pypowsybl.network as pn
import pytest

from yagat.app_context import AppContext


class TestListener:

    __test__ = False

    def __init__(self, context: AppContext):
        self._status_text_from_listener = None
        self._network_from_listener = None
        self._selection_from_listener = None
        self._selected_tab_from_listener = None
        context.add_status_text_listener(lambda value: self.status_text_listener(value))
        context.add_network_changed_listener(lambda value: self.network_listener(value))
        context.add_selection_changed_listener(lambda value: self.selection_listener(value))
        context.add_tab_changed_listener(lambda value: self.selected_tab_listener(value))

    def status_text_listener(self, value):
        self._status_text_from_listener = value

    def network_listener(self, value):
        self._network_from_listener = value

    def selection_listener(self, value):
        self._selection_from_listener = value

    def selected_tab_listener(self, value):
        self._selected_tab_from_listener = value

    @property
    def status_text_from_listener(self):
        return self._status_text_from_listener

    @property
    def network_from_listener(self) -> pn.Network:
        return self._network_from_listener

    @property
    def selection_from_listener(self):
        return self._selection_from_listener

    @property
    def selected_tab_from_listener(self):
        return self._selected_tab_from_listener


class TestAppContext:

    @pytest.fixture
    def context(self):
        context = AppContext(tk.Tk())
        yield context

    def test_initial_state(self, context):
        assert context.tk_root is not None
        assert context.network is None
        assert context.network_structure is None
        assert context.selection[0] is None
        assert context.selection[1] is None
        assert context.selection[2] is None
        assert context.status_text == 'Welcome'

    def test_status_text(self, context):
        test = TestListener(context)
        context.status_text = 'test status text'
        assert test.status_text_from_listener == 'test status text'

    def test_network(self, context):
        test = TestListener(context)
        context.network = pn.create_ieee9()
        assert test.network_from_listener.name == 'ieee9cdf'
        context.network = None
        assert test.network_from_listener is None

    def test_selection(self, context):
        test = TestListener(context)
        context.selection = 'test selection'
        assert test.selection_from_listener == 'test selection'
        context.selection = None
        assert test.selection_from_listener is None

    def test_selected_tab(self, context):
        test = TestListener(context)
        context.selected_tab = 'test selected tab'
        assert test.selected_tab_from_listener == 'test selected tab'
        context.selected_tab = None
        assert test.selected_tab_from_listener is None
