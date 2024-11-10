#
# Copyright (c) 2024, Damien Jeandemange (https://github.com/jeandemanged)
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
# SPDX-License-Identifier: MPL-2.0
#
import os
import tkinter as tk

from yagat import get_app_path, __version__
from yagat.utils import get_centered_geometry


class SplashScreen(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        parent.overrideredirect(True)
        parent.geometry(get_centered_geometry(parent, 403, 302))
        splash_canvas = tk.Canvas(parent)
        splash_canvas.pack(fill="both", expand=True)
        self.img = tk.PhotoImage(file=os.path.join(get_app_path(), 'images/splash.png'))
        splash_canvas.create_image(0, 0, image=self.img, anchor=tk.NW)
        splash_canvas.create_text(10, 10, text='Yet Another Grid Analysis Tool', fill="black", anchor=tk.NW)
        splash_canvas.create_text(10, 30, text=f'YAGAT v{__version__}', fill="black", anchor=tk.NW)


if __name__ == "__main__":
    root = tk.Tk()
    SplashScreen(root)
    root.mainloop()
