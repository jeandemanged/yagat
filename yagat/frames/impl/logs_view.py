#
# Copyright (c) 2024, Damien Jeandemange (https://github.com/jeandemanged)
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
# SPDX-License-Identifier: MPL-2.0
#
import logging
import tkinter as tk

import tksheet as tks


class LogsView(tk.Frame, logging.Handler):

    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        logging.Handler.__init__(self)
        logger = logging.getLogger()
        logger.addHandler(self)
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
        self.sheet.pack(fill="both", expand=True)

    def emit(self, record):
        msg = self.format(record)
        self.sheet.insert_row(row=[record.asctime, record.levelname, msg], idx=0)
        self.sheet.set_all_cell_sizes_to_text()
