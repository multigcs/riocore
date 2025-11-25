import os
import sys

import hal
from PyQt5.QtWidgets import QDialog
from PyQt5.uic import loadUi

# called by dialogs.manual_tool_change


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

        tc_ui_path = os.path.join(self.gui_path, "tool_change.ui")
        loadUi(tc_ui_path, self)
        tool = hal.get_value("iocontrol.0.tool-prep-number")
        if tool:
            self.tool_change_lb.setText(f"Insert Tool #{tool}\nPress OK when Done")
        else:
            self.tool_change_lb.setText("Remove Tool From Spindle\nPress OK when Done")
