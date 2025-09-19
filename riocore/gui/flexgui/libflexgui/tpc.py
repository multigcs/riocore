# Three Point Center Calculator

import os
import sys

from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QPixmap
from PyQt6.uic import loadUi

import linuxcnc as emc

# from libflexgui import utilities
# from libflexgui import dialogs


class tpc_calc(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.path = os.path.dirname(os.path.realpath(sys.argv[0]))
        if self.path == "/usr/bin":
            self.lib_path = "/usr/lib/libflexgui"
        else:
            self.lib_path = os.path.join(self.path, "libflexgui")
        loadUi(os.path.join(self.lib_path, "tpc.ui"), self)
        image_path = os.path.join(self.lib_path, "tpc.jpg")
        print(image_path)
        pixmap = QPixmap(image_path)
        self.tpc_lb.setPixmap(pixmap)
        self.tpc_lb.setScaledContents(True)

        self.stat = emc.stat()

        self.save_point_1_pb.clicked.connect(self.save_point_1)
        self.save_point_2_pb.clicked.connect(self.save_point_2)
        self.save_point_3_pb.clicked.connect(self.save_point_3)
        self.calculate_center_pb.clicked.connect(self.calculate_center)
        self.move_to_center_pb.clicked.connect(self.move_to_center)
        self.set_to_x0_y0.clicked.connect(self.set_to_x0y0)

        self.x1 = 0.0
        self.y1 = 0.0
        self.x2 = 0.0
        self.y2 = 0.0
        self.x3 = 0.0
        self.y3 = 0.0

    def save_point_1(self):
        self.stat.poll()
        self.x1 = self.stat.joint_position[0]
        self.y1 = self.stat.joint_position[1]
        self.point_1_x.setText(f"{self.x1:.4f}")
        self.point_1_y.setText(f"{self.y1:.4f}")

    def save_point_2(self):
        self.stat.poll()
        self.x2 = self.stat.joint_position[0]
        self.y2 = self.stat.joint_position[1]
        self.point_2_x.setText(f"{self.x2:.4f}")
        self.point_2_y.setText(f"{self.y2:.4f}")

    def save_point_3(self):
        self.stat.poll()
        self.x3 = self.stat.joint_position[0]
        self.y3 = self.stat.joint_position[1]
        self.point_3_x.setText(f"{self.x3:.4f}")
        self.point_3_y.setText(f"{self.y3:.4f}")

    def calculate_center(self):
        x1 = self.x1
        y1 = self.y1
        x2 = self.x2
        y2 = self.y2
        x3 = self.x3
        y3 = self.y3

        try:
            x_center = ((x1**2 + y1**2) * (y2 - y3) + (x2**2 + y2**2) * (y3 - y1) + (x3**2 + y3**2) * (y1 - y2)) / (2 * (x1 * (y2 - y3) - y1 * (x2 - x3) + x2 * y3 - x3 * y2))
            y_center = ((x1**2 + y1**2) * (x3 - x2) + (x2**2 + y2**2) * (x1 - x3) + (x3**2 + y3**2) * (x2 - x1)) / (2 * (x1 * (y2 - y3) - y1 * (x2 - x3) + x2 * y3 - x3 * y2))
            self.center_x.setText(f"{x_center:.4f}")
            self.center_y.setText(f"{y_center:.4f}")
        except Exception as e:
            # Print the type of the exception
            print("Type of Exception:", type(e))
            # Print the specific error message
            print("Error Message:", e)

    def move_to_center(self):
        print("move_to_center")

    def set_to_x0y0(self):
        print("set_to_x0y0")
