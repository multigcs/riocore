import sys
import os

from PyQt5.QtWidgets import QDialog
from PyQt5.uic import loadUi

# called by dialogs.tool_touchoff_selected


class app(QDialog):
    def __init__(self):
        super().__init__()

        self.path = os.path.dirname(os.path.realpath(sys.argv[0]))
        # set the library path
        if self.path == "/usr/bin":
            self.lib_path = "/usr/lib/libflexgui"
            self.gui_path = "/usr/lib/libflexgui"
        else:
            self.lib_path = os.path.join(self.path, "libflexgui")
            self.gui_path = self.path

        tto_ui_path = os.path.join(self.gui_path, "tool_touchoff.ui")
        loadUi(tto_ui_path, self)
