import os
import hashlib
import sys

import riocore


from PyQt5.QtWidgets import (
    QPlainTextEdit,
    QTabWidget,
)

from riocore.widgets import (
    STYLESHEET_TABBAR,
)


class TabGateware:
    def __init__(self, parent=None):
        self.parent = parent
        self.gateware = {
            "rio.v": QPlainTextEdit(),
            "Makefile": QPlainTextEdit(),
            "Compile-Output": QPlainTextEdit(),
            "Flash-Output": QPlainTextEdit(),
        }
        self.gateware_tabwidget = QTabWidget()
        self.gateware_tabwidget.setStyleSheet(STYLESHEET_TABBAR)
        for filename, widget in self.gateware.items():
            widget.clear()
            widget.insertPlainText("")
            self.gateware_tabwidget.addTab(widget, filename)

    def setTab(self, name):
        self.gateware_tabwidget.setCurrentWidget(self.gateware[name])

    def widget(self):
        return self.gateware_tabwidget

    def timer(self):
        pass

    def update(self):
        config_name = self.parent.config.get("name")

        for filename, widget in self.gateware.items():
            if not filename.endswith("-Output"):
                file_content = open(os.path.join(self.parent.output_path, config_name, "Gateware", filename), "r").read()
                widget.clear()
                widget.insertPlainText(file_content)
                if filename == "rio.v":
                    hash_md5 = hashlib.md5()
                    with open(os.path.join(self.parent.output_path, config_name, "Gateware", filename), "rb") as f:
                        for chunk in iter(lambda: f.read(4096), b""):
                            hash_md5.update(chunk)
                    self.parent.gateware_hash = hash_md5.hexdigest()
