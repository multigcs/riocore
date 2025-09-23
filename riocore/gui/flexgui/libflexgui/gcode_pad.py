import sys
import os

from PyQt5.QtWidgets import QDialog, QPushButton
from PyQt5.uic import loadUi


class gcode_pad(QDialog):
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

        num_ui_path = os.path.join(self.gui_path, "gcode.ui")
        loadUi(num_ui_path, self)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
        self.clear_pb.clicked.connect(self.clear)
        self.backspace_pb.clicked.connect(self.backspace)

        for item in self.findChildren(QPushButton):
            if item.objectName().startswith("char_"):
                getattr(self, f"{item.objectName()}").clicked.connect(self.post)
            elif item.objectName().startswith("next_"):
                getattr(self, f"{item.objectName()}").clicked.connect(self.next)
            elif item.objectName().startswith("back_"):
                getattr(self, f"{item.objectName()}").clicked.connect(self.back)

    def next(self):
        self.letters_sw.setCurrentIndex(self.letters_sw.currentIndex() + 1)

    def back(self):
        self.letters_sw.setCurrentIndex(self.letters_sw.currentIndex() - 1)

    def post(self):
        txt = self.gcode_lb.text()
        self.gcode_lb.setText(f"{txt}{self.sender().text()}")

    def clear(self):
        self.gcode_lb.clear()

    def backspace(self):
        txt = self.gcode_lb.text()
        if len(txt) > 0:
            self.gcode_lb.setText(txt[:-1])

    def retval(self):
        try:
            return self.gcode_lb.text()
        except Exception:
            return False
