#
# Copyright (c) 2024, Damien Jeandemange (https://github.com/jeandemanged)
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
# SPDX-License-Identifier: MPL-2.0
#
import tkinter as tk
from tkinter import ttk


# https://stackoverflow.com/questions/16188420/tkinter-scrollbar-for-frame
# Based on
#   https://web.archive.org/web/20170514022131id_/http://tkinter.unpythonic.net/wiki/VerticalScrolledFrame

class VerticalScrolledFrame(ttk.Frame):
    """A pure Tkinter scrollable frame that actually works!
    * Use the 'interior' attribute to place widgets inside the scrollable frame.
    * Construct and pack/place/grid normally.
    * This frame only allows vertical scrolling.
    """

    def __init__(self, parent, *args, **kw):
        ttk.Frame.__init__(self, parent, *args, **kw)

        # Create a canvas object and a vertical scrollbar for scrolling it.
        self.vsb = ttk.Scrollbar(self, orient=tk.VERTICAL)
        self.vsb.pack(fill=tk.Y, side=tk.RIGHT, expand=tk.FALSE)
        self.canvas = canvas = tk.Canvas(self, bd=0, highlightthickness=0,
                                         yscrollcommand=self.vsb.set)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=tk.TRUE)
        self.vsb.config(command=canvas.yview)

        # Reset the view
        canvas.xview_moveto(0)
        canvas.yview_moveto(0)

        events = ['<MouseWheel>', '<Button-4>', '<Button-5>']

        def bind():
            for e in events:
                canvas.bind_all(e, self._on_mousewheel)

        def unbind():
            for e in events:
                canvas.unbind_all(e)

        # Activate / deactivate mousewheel scrolling when cursor is over / not over the canvas.
        canvas.bind("<Enter>", lambda _: bind())
        canvas.bind("<Leave>", lambda _: unbind())

        # Create a frame inside the canvas which will be scrolled with it.
        self.interior = interior = ttk.Frame(canvas)
        interior_id = canvas.create_window(0, 0, window=interior,
                                           anchor=tk.NW)

        # Track changes to the canvas and frame width and sync them,
        # also updating the scrollbar.
        def _configure_interior(event):
            # Update the scrollbars to match the size of the inner frame.
            size = (interior.winfo_reqwidth(), interior.winfo_reqheight())
            canvas.config(scrollregion="0 0 %s %s" % size)
            if interior.winfo_reqwidth() != canvas.winfo_width():
                # Update the canvas's width to fit the inner frame.
                canvas.config(width=interior.winfo_reqwidth())

        interior.bind('<Configure>', _configure_interior)

        def _configure_canvas(event):
            if interior.winfo_reqwidth() != canvas.winfo_width():
                # Update the inner frame's width to fill the canvas.
                canvas.itemconfigure(interior_id, width=canvas.winfo_width())

        canvas.bind('<Configure>', _configure_canvas)

    def _on_mousewheel(self, event):
        y1, y2 = self.vsb.get()
        direction = 0
        # linux / windows / macOS
        if event.num == 5 or event.delta == -120 or event.delta == -1:
            direction = +1
        if event.num == 4 or event.delta == 120 or event.delta == 1:
            direction = -1
        if y1 != 0 or y2 != 1:
            self.canvas.yview_scroll(direction, "units")


if __name__ == "__main__":

    class SampleApp(tk.Tk):
        def __init__(self, *args, **kwargs):
            tk.Tk.__init__(self, *args, **kwargs)

            self.frame = VerticalScrolledFrame(self)
            self.frame.pack()
            self.label = ttk.Label(self, text="Shrink the window to activate the scrollbar.")
            self.label.pack()
            buttons = []
            for i in range(10):
                buttons.append(ttk.Button(self.frame.interior, text="Button " + str(i)))
                buttons[-1].pack()


    app = SampleApp()
    app.mainloop()
