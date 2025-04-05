import os
import sys

if os.path.isfile(os.path.join("riocore", "__init__.py")):
    sys.path.insert(0, os.getcwd())
elif os.path.isfile(os.path.join(os.path.dirname(os.path.dirname(__file__)), "riocore", "__init__.py")):
    sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import riocore


from PyQt5.QtWidgets import (
    QPlainTextEdit,
    QTabWidget,
)

from riocore.widgets import (
    STYLESHEET_TABBAR,
)


riocore_path = os.path.dirname(riocore.__file__)


class TabLinuxCNC:
    def __init__(self, parent=None):
        self.parent = parent
        self.linuxcnc = {
            "rio.ini": QPlainTextEdit(),
            "rio.hal": QPlainTextEdit(),
            "custom_postgui.hal": QPlainTextEdit(),
            "rio-gui.xml": QPlainTextEdit(),
            "riocomp.c": QPlainTextEdit(),
        }
        self.linuxcnc_tabwidget = QTabWidget()
        self.linuxcnc_tabwidget.setStyleSheet(STYLESHEET_TABBAR)
        for filename, widget in self.linuxcnc.items():
            widget.clear()
            widget.insertPlainText("")
            self.linuxcnc_tabwidget.addTab(widget, filename)

    def setTab(self, name):
        self.linuxcnc_tabwidget.setCurrentWidget(self.linuxcnc[name])

    def widget(self):
        return self.linuxcnc_tabwidget

    def timer(self):
        pass

    def update(self):
        config_name = self.parent.config.get("name")
        for filename, widget in self.linuxcnc.items():
            widget.clear()
            file_path = os.path.join(self.parent.output_path, config_name, "LinuxCNC", filename)
            if os.path.isfile(file_path):
                file_content = open(file_path, "r").read()
                widget.insertPlainText(file_content)

                if filename == "rio-gui.xml" and self.parent.vcp is not None:
                    self.parent.vcp.load(file_path)
