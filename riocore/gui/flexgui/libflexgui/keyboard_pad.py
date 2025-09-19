import sys
import os
from functools import partial

from PyQt6.QtWidgets import QDialog, QPushButton
from PyQt6.uic import loadUi


class keyboard_pad(QDialog):
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

        loadUi(os.path.join(self.gui_path, "keyboard.ui"), self)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
        self.clear_pb.clicked.connect(self.clear)
        self.space_pb.clicked.connect(self.space)
        self.backspace_pb.clicked.connect(self.backspace)
        self.gcode_pb.clicked.connect(partial(self.change_page, 0))
        self.capital_letters_pb.clicked.connect(partial(self.change_page, 1))
        self.lower_letters_pb.clicked.connect(partial(self.change_page, 2))
        self.symbols_pb.clicked.connect(partial(self.change_page, 3))

        for item in self.findChildren(QPushButton):
            if item.objectName().startswith("key_"):
                getattr(self, f"{item.objectName()}").clicked.connect(self.post)

    def post(self):
        txt = self.keyboard_lb.text()
        self.keyboard_lb.setText(f"{txt}{self.sender().text()}")

    def clear(self):
        self.keyboard_lb.clear()

    def space(self):
        txt = self.keyboard_lb.text()
        self.keyboard_lb.setText(f"{txt} ")

    def backspace(self):
        txt = self.keyboard_lb.text()
        if len(txt) > 0:
            self.keyboard_lb.setText(txt[:-1])

    def change_page(self, index):
        self.keyboard_sw.setCurrentIndex(index)

    def retval(self):
        try:
            return self.keyboard_lb.text()
        except Exception:
            return False
