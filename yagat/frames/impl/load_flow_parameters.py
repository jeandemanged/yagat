#
# Copyright (c) 2024, Damien Jeandemange (https://github.com/jeandemanged)
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
# SPDX-License-Identifier: MPL-2.0
#
import idlelib.tooltip as itooltip
import logging
import os
import textwrap
import tkinter as tk
from tkinter import ttk

import pypowsybl.loadflow as lf

from yagat.app_context import AppContext
from yagat.frames.impl.vertical_scrolled_frame import VerticalScrolledFrame


class LoadFlowParametersView(VerticalScrolledFrame):

    def __init__(self, parent, context: AppContext, *args, **kwargs):
        VerticalScrolledFrame.__init__(self, parent, *args, **kwargs)
        self.context = context
        self.variables = []

        i_row = -1

        for param_idx, param_s in lf.get_provider_parameters().iterrows():
            i_col = -1
            i_row += 1
            param_name = str(param_idx)
            param_description = param_s.description
            param_type = param_s.type
            param_default = param_s.default
            if param_default == '[]':
                param_default = ''
            param_possible_values = None
            if param_s.possible_values and param_s.possible_values != '[]':
                param_possible_values = param_s.possible_values[1:-1].split(', ')

            name_label = tk.Label(self.interior, text=param_name)
            i_col += 1
            name_label.grid(row=i_row, column=i_col, sticky=tk.E, padx=10)
            itooltip.Hovertip(name_label, '\n'.join(textwrap.wrap(param_description)), hover_delay=100)

            i_col += 1
            if param_type == 'BOOLEAN':
                var = tk.IntVar()
                self.variables.append(var)
                init_val = 0
                if param_default == 'true':
                    init_val = 1
                var.set(init_val)
                check = ttk.Checkbutton(self.interior, variable=var, onvalue=1, offvalue=0, command=lambda k=param_name, v=var: self.value_update(k, v))
                check.grid(row=i_row, column=i_col, sticky=tk.W)
            elif param_type == 'STRING':
                var = tk.StringVar()
                self.variables.append(var)
                var.set(param_default)
                var.trace_add("write", callback=lambda _1, _2, _3, k=param_name, v=var: self.value_update(k, v))
                if param_possible_values:
                    widget = ttk.Combobox(self.interior, textvariable=var, state='readonly', values=param_possible_values)
                else:
                    widget = ttk.Entry(self.interior, textvariable=var)
                widget.grid(row=i_row, column=i_col, sticky=tk.W+tk.E)
            elif param_type == 'STRING_LIST':
                if param_possible_values:
                    # FIXME: possibility of reordering (voltageTargetPriorities)
                    list_box = tk.Listbox(self.interior, selectmode=tk.MULTIPLE, exportselection=False)
                    i = -1
                    for p in param_possible_values:
                        i += 1
                        list_box.insert(tk.END, p)
                        if p in param_default:
                            list_box.selection_set(i)
                    list_box.bind('<<ListboxSelect>>', func=lambda event, k=param_name: self.list_box_update(event, k))
                    list_box.grid(row=i_row, column=i_col, sticky=tk.W+tk.E)
                else:
                    var = tk.StringVar()
                    self.variables.append(var)
                    var.set(param_default)
                    var.trace_add("write", callback=lambda _1, _2, _3, k=param_name, v=var: self.value_update(k, v))
                    entry = ttk.Entry(self.interior, textvariable=var)
                    entry.grid(row=i_row, column=i_col, sticky=tk.W+tk.E)
            elif param_type == 'INTEGER' or param_type == 'DOUBLE':
                var = tk.StringVar()
                self.variables.append(var)
                var.set(param_default)
                var.trace_add("write", callback=lambda _1, _2, _3, k=param_name, v=var: self.value_update(k, v))
                entry = ttk.Entry(self.interior, textvariable=var)
                entry.grid(row=i_row, column=i_col, sticky=tk.W)

        self.interior.columnconfigure(0)
        self.interior.columnconfigure(1, minsize=300)

    def value_update(self, k: str, v):
        value = v.get()
        if isinstance(v, tk.IntVar):
            if value:
                value = 'true'
            else:
                value = 'false'
        if value:
            self.context.lf_parameters.provider_parameters[k] = value
            logging.info(f'Load Flow Parameter "{k}" set to {value}')

    def list_box_update(self, event, k):
        updated_widget = event.widget
        selected_indexes = list(event.widget.curselection())
        all_items = updated_widget.get(0, tk.END)
        selected_items = []
        for i in selected_indexes:
            selected_items.append(all_items[i])
        value = ','.join(selected_items)
        self.context.lf_parameters.provider_parameters[k] = value
        logging.info(f'Load Flow Parameter "{k}" set to {value}')


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
