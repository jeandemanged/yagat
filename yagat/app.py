#
# Copyright (c) 2024, Damien Jeandemange (https://github.com/jeandemanged)
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
# SPDX-License-Identifier: MPL-2.0
#
import logging
import os
import tkinter as tk

from yagat import get_app_path
from yagat.frames import SplashScreen, MainApplication

logging.getLogger('powsybl').setLevel(logging.INFO)
logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)

if __name__ == "__main__":

    splash_root = tk.Tk()
    splash_root.iconphoto(True, tk.PhotoImage(file=os.path.join(get_app_path(), 'images/logo.png')))


    def main_window():
        splash_root.destroy()
        root = tk.Tk()

        # Remove ttk Combobox Mousewheel Binding, see https://stackoverflow.com/questions/44268882/remove-ttk-combobox-mousewheel-binding
        root.unbind_class("TCombobox", "<MouseWheel>")  # Windows & OSX
        root.unbind_class("TCombobox", "<ButtonPress-4>")  # Linux and other *nix systems
        root.unbind_class("TCombobox", "<ButtonPress-5>")  # Linux and other *nix systems

        MainApplication(root)
        root.mainloop()


    if os.name == 'nt':
        # Fixing the blur UI on Windows
        from ctypes import windll

        windll.shcore.SetProcessDpiAwareness(2)

    splash = SplashScreen(splash_root)
    splash.after(1500, main_window)
    splash_root.mainloop()
