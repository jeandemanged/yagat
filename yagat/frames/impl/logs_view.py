#
# Copyright (c) 2024, Damien Jeandemange (https://github.com/jeandemanged)
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
# SPDX-License-Identifier: MPL-2.0
#
import logging
import queue
import tkinter as tk

import tksheet as tks
from pypowsybl import _pypowsybl

# to be made configurable some day
MAX_LOG_ROWS = 2000

# how often we check for messages in the queue in milliseconds
_LISTEN_LOOP_MS = 100

# delay before redrawing sheet
_AFTER_REDRAW_TIME_MS = 500


class LogsView(tk.Frame, logging.Handler):

    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        logging.Handler.__init__(self)
        logger = logging.getLogger()
        logger.addHandler(self)
        self.sheet = tks.Sheet(self, index_align='left', after_redraw_time_ms=_AFTER_REDRAW_TIME_MS)
        self.sheet.hide(canvas="top_left")
        self.sheet.hide(canvas="row_index")
        self.sheet.font(
            newfont=("Courier", 12, "normal"))  # not the best monospaced font but should work on all platforms
        self.sheet.set_header_data(c=0, value="Time")
        self.sheet.set_column_widths([240, 90, 800])  # tksheet has typehint issue here but works
        self.sheet.set_header_data(c=1, value="Level")
        self.sheet.set_header_data(c=2, value="Message")
        self.sheet['A:C'].readonly(readonly=True)
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
                                   'row_height_resize',
                                   'column_height_resize',
                                   'arrowkeys',
                                   )
        self.sheet.pack(fill="both", expand=True)
        self.log_queue = queue.Queue()
        self.after(_LISTEN_LOOP_MS, self.listen_queue)  # start listen loop
        logging.info(_pypowsybl.get_version_table())

    def emit(self, record):
        self.log_queue.put(record)

    def listen_queue(self):
        while self.log_queue.qsize():
            try:
                record = self.log_queue.get()
                msg = self.format(record)
                self.sheet.insert_row(row=[record.asctime, record.levelname, msg], idx=0)
                if record.levelname == 'WARNING':
                    self.sheet[0:1].highlight(bg='gold', redraw=False)
                elif record.levelname == 'ERROR':
                    self.sheet[0:1].highlight(bg='salmon', redraw=False)
                if len(self.sheet.data) > MAX_LOG_ROWS:
                    self.sheet.delete_row(idx=MAX_LOG_ROWS, redraw=False)
                self.sheet.set_cell_size_to_text(row=0, column=2, only_set_if_too_small=True)
            except queue.Empty:
                pass
        # re-listen
        self.after(_LISTEN_LOOP_MS, self.listen_queue)
