import os
import sys

import riocore


from PyQt5.QtWidgets import (
    QPlainTextEdit,
    QTabWidget,
)

from riocore.widgets import (
    STYLESHEET_TABBAR,
)


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
        self.tabwidget = QTabWidget()
        self.tabwidget.setStyleSheet(STYLESHEET_TABBAR)
        for filename, widget in self.linuxcnc.items():
            widget.clear()
            widget.insertPlainText("")
            self.tabwidget.addTab(widget, filename)

    def setTab(self, name):
        self.tabwidget.setCurrentWidget(self.linuxcnc[name])

    def widget(self):
        return self.tabwidget

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
