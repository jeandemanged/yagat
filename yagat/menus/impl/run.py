#
# Copyright (c) 2024, Damien Jeandemange (https://github.com/jeandemanged)
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
# SPDX-License-Identifier: MPL-2.0
#
import tkinter as tk

import pypowsybl.loadflow as lf
import pypowsybl.report as pr

from yagat.app_context import AppContext


class RunMenu(tk.Menu):
    def __init__(self, parent, context: AppContext, *args, **kwargs):
        tk.Menu.__init__(self, parent, *args, **kwargs)

        self.parent = parent
        self.context = context
        parent.add_cascade(label="Run", menu=self)
        self.add_command(label='AC Load Flow', command=lambda: self.run_load_flow(ac=True))
        self.add_command(label='DC Load Flow', command=lambda: self.run_load_flow(ac=False))

    def run_load_flow(self, ac: bool):
        reporter = pr.Reporter()
        self.context.status_text = 'Starting Load Flow'

        def on_done():
            self.context.network_structure.refresh()
            self.context.notify_selection_changed()  # hack to trigger refresh
            self.context.status_text = 'Load Flow completed'

        def task():
            if ac:
                results = lf.run_ac(self.context.network, parameters=self.context.lf_parameters, reporter=reporter)
            else:
                results = lf.run_dc(self.context.network, parameters=self.context.lf_parameters, reporter=reporter)
            print(results)
            print(reporter)

        self.context.start_long_running_task(name='Load Flow', target=task, on_done=on_done)
