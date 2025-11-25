import os
import sys

from PyQt5.QtWidgets import QDialog
from PyQt5.uic import loadUi


class number_pad(QDialog):
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

        num_ui_path = os.path.join(self.gui_path, "numbers.ui")
        loadUi(num_ui_path, self)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
        self.clear_pb.clicked.connect(self.clear)
        self.dot_pb.clicked.connect(self.dot)
        self.dash_pb.clicked.connect(self.dash)
        self.backspace_pb.clicked.connect(self.backspace)
        for i in range(10):
            getattr(self, f"num_pb_{i}").clicked.connect(self.post)

    def post(self):
        txt = self.numbers_lb.text()
        self.numbers_lb.setText(f"{txt}{self.sender().objectName()[-1]}")

    def clear(self):
        self.numbers_lb.clear()

    def dot(self):
        txt = self.numbers_lb.text()
        self.numbers_lb.setText(f"{txt}.")

    def dash(self):
        txt = self.numbers_lb.text()
        self.numbers_lb.setText(f"-{txt}")

    def backspace(self):
        txt = self.numbers_lb.text()
        if len(txt) > 0:
            self.numbers_lb.setText(txt[:-1])

    def retval(self):
        try:
            return self.numbers_lb.text()
        except Exception:
            return False
