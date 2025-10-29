#!/usr/bin/env python3
#
#

import sys
from functools import partial
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QDoubleSpinBox,
    QHBoxLayout,
    QLabel,
    QVBoxLayout,
    QWidget,
)

from PyQt5.QtCore import QRectF, QRect, QTimer
from PyQt5.QtGui import QPainter, QPen, QBrush, QFont, QColor


class HomeAnimation(QWidget):
    def __init__(self, data):
        super().__init__()
        self.data = data
        self.width = 500
        self.height = 200
        self.setFixedWidth(self.width)
        self.setFixedHeight(self.height)

        self.zero = self.width // 2
        self.start_pos = 100

        self.used_speed = ""
        self.invert = 1
        self.steps = 0
        self.sequence = 0
        self.slider_pos = self.start_pos
        self.delay = 10

        self.runTimer()
        self.timer = QTimer()
        self.timer.timeout.connect(self.runTimer)
        self.timer.start(50)

    def runTimer(self):
        # HOME = self.data["HOME"]["value"]
        HOME_SEARCH_VEL = self.data["HOME_SEARCH_VEL"]["value"]
        # MIN_LIMIT = self.data["MIN_LIMIT"]["value"]
        # MAX_LIMIT = self.data["MAX_LIMIT"]["value"]

        self.invert = 1
        if HOME_SEARCH_VEL > 0:
            self.invert = -1

        self.data["HOME_SEARCH_VEL"]["label"].setStyleSheet("QLabel { color : black; }")
        self.data["HOME_LATCH_VEL"]["label"].setStyleSheet("QLabel { color : black; }")
        self.data["HOME_FINAL_VEL"]["label"].setStyleSheet("QLabel { color : black; }")
        # speed = 0
        if f"HOME_{self.used_speed}_VEL" in self.data:
            # speed = abs(self.data[f"HOME_{self.used_speed}_VEL"]["value"])
            self.data[f"HOME_{self.used_speed}_VEL"]["label"].setStyleSheet("QLabel { color : blue; }")

        """
        if self.steps > 0:
            self.parent.info.setText(f"{self.used_speed} ({speed} units/s) -->")
        elif self.steps < 0:
            self.parent.info.setText(f"{self.used_speed} ({speed} units/s) <--")
        else:
            self.parent.info.setText("")
        """

        """
        if not (MIN_LIMIT <= HOME <= MAX_LIMIT):
            self.parent.errors.setText("ERROR: HOME POSITION must between MIN_LIMIT and  MAX_LIMIT")
        elif abs(self.data["HOME_LATCH_VEL"]["value"]) >= abs(self.data["HOME_SEARCH_VEL"]["value"]):
            self.parent.errors.setText("INFO: HOME_LATCH_VEL should be lower than HOME_SEARCH_VEL")
        else:
            self.parent.errors.setText("")
        """

        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        self.draw_scale(painter, 60, 130)
        self.draw_motor(painter, 0, 30)
        self.draw_spindle(painter, 60, 30)

        HOME_SEARCH_VEL = self.data["HOME_SEARCH_VEL"]["value"]
        HOME_LATCH_VEL = self.data["HOME_LATCH_VEL"]["value"]
        HOME_OFFSET = self.data["HOME_OFFSET"]["value"]
        HOME = self.data["HOME"]["value"]
        MIN_LIMIT = self.data["MIN_LIMIT"]["value"]
        MAX_LIMIT = self.data["MAX_LIMIT"]["value"]

        if HOME_OFFSET > 0:
            if HOME < 0:
                self.home_sw_pos = 50
                self.home_pos = -50
            elif HOME > 0 and HOME > HOME_OFFSET:
                self.home_sw_pos = 50
                self.home_pos = 100
            elif HOME == HOME_OFFSET:
                self.home_sw_pos = 50
                self.home_pos = 50
            else:
                self.home_sw_pos = 50
                self.home_pos = 0
        elif HOME_OFFSET < 0:
            if HOME > 0:
                self.home_sw_pos = -50
                self.home_pos = 50
            elif HOME < 0 and HOME > HOME_OFFSET:
                self.home_sw_pos = -100
                self.home_pos = -50
            elif HOME == HOME_OFFSET:
                self.home_sw_pos = -50
                self.home_pos = -100
            else:
                self.home_sw_pos = -50
                self.home_pos = 0
        else:
            self.home_sw_pos = 0
            if HOME > 0:
                self.home_pos = 50
            elif HOME < 0:
                self.home_pos = -50
            else:
                self.home_pos = 0

        self.home_sw_pos *= self.invert
        self.home_pos *= self.invert

        if self.delay > 0:
            self.delay -= 1
        elif self.sequence == 0:
            self.used_speed = "SEARCH"
            if self.slider_pos > self.home_sw_pos:
                self.steps = -3
            else:
                self.steps = 0
                self.sequence = 1
                self.delay = 2

        elif self.sequence == 1 and HOME_LATCH_VEL > 0:  # HOME_LATCH_VEL+
            self.used_speed = "SEARCH"
            if self.slider_pos < self.home_sw_pos + 10:
                self.steps = 3
            else:
                self.steps = 0
                self.sequence = 2
                self.delay = 2
        elif self.sequence == 2:  # HOME_LATCH_VEL+
            self.used_speed = "LATCH"
            if self.slider_pos > self.home_sw_pos:
                self.steps = -1
            else:
                self.steps = 0
                self.sequence = 3
                self.delay = 2

        elif self.sequence == 1 and HOME_LATCH_VEL < 0:  # HOME_LATCH_VEL-
            self.used_speed = "LATCH"
            if self.slider_pos < self.home_sw_pos:
                self.steps = 1
            else:
                self.steps = 0
                self.sequence = 3
                self.delay = 2

        elif self.sequence == 3:
            self.used_speed = "FINAL"
            if self.home_pos > self.slider_pos:
                self.steps = int(min(10, abs(self.home_pos - self.slider_pos)))
            elif self.home_pos < self.slider_pos:
                self.steps = -int(min(10, abs(self.home_pos - self.slider_pos)))
            else:
                self.steps = 0
                self.sequence = 4
                self.delay = 30
                self.used_speed = ""

        else:
            self.used_speed = ""
            if self.slider_pos < self.start_pos:
                self.steps = 20
            else:
                self.steps = 0
                self.sequence = 0
                self.delay = 20

        self.slider_pos += self.steps

        # painter.setPen(QPen(Qt.black, 2))
        # painter.setFont(QFont("Arial", 12))
        # painter.drawText(QRectF(5, 60, 200, 20), Qt.AlignLeft, self.used_speed.title())

        self.draw_marker(painter, self.zero + self.home_sw_pos * self.invert, 130, HOME_OFFSET, "S", 1)
        self.draw_marker(painter, self.zero + self.home_pos * self.invert, 130, HOME, "H", 2)
        self.draw_slider(painter, self.zero + self.slider_pos * self.invert, 30)
        self.draw_switch(painter, self.zero + self.home_sw_pos * self.invert, 70, True)

        # soft limits
        if HOME_SEARCH_VEL > 0:
            if MIN_LIMIT < 0:
                zero_x = -150
                self.draw_marker(painter, self.zero - 160, 130, MIN_LIMIT, "-L", 2)
            elif MIN_LIMIT > 0:
                zero_x = 150
                self.draw_marker(painter, self.zero - 150, 130, MIN_LIMIT, "-L", 2)
            else:
                zero_x = -160
                self.draw_marker(painter, self.zero - 160, 130, MIN_LIMIT, "-L", 2)
        else:
            zero_x = 0
            self.draw_marker(painter, self.zero - 160, 130, MIN_LIMIT, "-L", 2)
        self.draw_marker(painter, self.zero + 200, 130, MAX_LIMIT, "+L", 2)

        # zero
        if self.sequence > 2:
            self.draw_marker(painter, self.zero + zero_x, 130, 0.0, "Z", 1)

        # limit switches
        self.draw_switch(painter, self.zero - 170, 70)
        self.draw_switch(painter, self.zero + 210, 70)

    def draw_marker(self, painter, x, y, value, text, level=1):
        painter.setFont(QFont("Arial", 11))
        painter.setPen(QPen(Qt.black, 1))
        if value is not None:
            painter.drawText(QRectF(x - 20, y, 40, 50), Qt.AlignCenter, str(value))
        if text:
            painter.drawText(QRectF(x - 50, y + 20 * level, 100, 50), Qt.AlignCenter, text)
        painter.setPen(QPen(Qt.blue, 1))
        painter.drawLine(x, 5, x, y + 15)

    def draw_scale(self, painter, x, y):
        painter.setFont(QFont("Arial", 10))
        painter.setPen(QPen(Qt.black, 1))
        painter.drawLine(x - 10, y, x + 500, y)
        for px in range(-10, 505, 5):
            painter.drawLine(x + px, y - 10, x + px, y)
        for px in range(-10, 505, 50):
            painter.drawLine(x + px, y - 20, x + px, y)
            # painter.drawText(QRectF(x + px - 20, y + 2, 40, 20), Qt.AlignCenter, f"{(px - 200) / 10}")

    def draw_slider(self, painter, x, y):
        width = 40
        height = 40
        x -= width // 2
        y -= height // 2
        painter.setPen(QPen(Qt.black, 2))
        painter.setBrush(QBrush(QColor.fromRgb(150, 150, 150)))
        painter.drawRect(x, y, width, height)
        painter.drawRect(x + width // 2 - 5, y + height, 10, 10)

    def draw_switch(self, painter, x, y, trigger=False):
        x -= 5
        painter.setPen(QPen(Qt.black, 2))
        painter.setBrush(QBrush(QColor.fromRgb(150, 150, 150)))
        painter.drawRect(x, y, 40, 20)
        painter.setBrush(QBrush(QColor.fromRgb(255, 255, 255)))
        # holes
        painter.drawEllipse(QRect(x + 2, y + 2, 7, 7))
        painter.drawEllipse(QRect(x + 31, y + 10, 7, 7))
        # sense
        painter.setPen(QPen(Qt.black, 2))
        if trigger:
            if self.invert > 0 and self.slider_pos < (x - self.zero) + 6:
                painter.setPen(QPen(Qt.red, 2))
            elif self.invert < 0 and self.slider_pos * self.invert > (x - self.zero) + 1:
                painter.setPen(QPen(Qt.red, 2))
        painter.drawLine(x, y - 5, x + 38, y)
        painter.drawLine(x - 5, y - 3, x, y - 5)
        # pins
        painter.setPen(QPen(Qt.black, 2))
        painter.drawLine(x + 2, y + 20, x + 2, y + 27)
        painter.drawLine(x + 10, y + 20, x + 10, y + 27)
        painter.drawLine(x + 36, y + 20, x + 36, y + 27)

    def draw_spindle(self, painter, x, y):
        width = 500
        height = 10
        y -= height // 2
        painter.setPen(QPen(Qt.black, 2))
        painter.setBrush(QBrush(QColor.fromRgb(100, 100, 100)))
        painter.drawRect(x, y, width, height)

    def draw_motor(self, painter, x, y):
        width = 50
        height = 50
        y -= height // 2

        painter.setPen(QPen(Qt.black, 2))
        painter.setBrush(QBrush(QColor.fromRgb(100, 100, 100)))
        # body
        painter.drawRect(x + 5 + 10, y + 2, width - 5 - 10 - 10, height - 4)
        # axis
        painter.drawRect(x + width, y + height // 2 - 3, 20, 6)
        # back
        painter.setBrush(QBrush(QColor.fromRgb(150, 150, 150)))
        painter.drawRect(x + 5, y, 10, 50)
        # front
        painter.drawRect(x + width - 10, y, 10, 50)
        # bolts
        painter.setBrush(QBrush(QColor.fromRgb(70, 70, 70)))
        painter.drawRect(x, y + 4, 5, 5)
        painter.drawRect(x, y + height - 4 - 5, 5, 5)


if __name__ == "__main__":

    class MainWindow(QMainWindow):
        def __init__(self):
            super().__init__()
            self.setWindowTitle("My App")

            self.setup = {
                "HOME_SEARCH_VEL": {"value": -30.0, "unit": "units/s"},
                "HOME_LATCH_VEL": {"value": 5.0, "unit": "units/s"},
                "HOME_FINAL_VEL": {"value": 100.0, "unit": "units/s"},
                "HOME_OFFSET": {"value": -1.0, "unit": "units"},
                "HOME": {"value": 2.0, "unit": "units"},
                "MIN_LIMIT": {"value": 0.0, "unit": "units"},
                "MAX_LIMIT": {"value": 500.0, "unit": "units"},
            }

            def update(key, value):
                self.setup[key]["value"] = value

            vbox = QVBoxLayout()
            for key, setup in self.setup.items():
                hbox = QHBoxLayout()
                setup["label"] = QLabel(key.title())
                hbox.addWidget(setup["label"], stretch=3)
                setup["widget"] = QDoubleSpinBox()
                setup["widget"].setMinimum(-99999.0)
                setup["widget"].setMaximum(99999.0)
                setup["widget"].setDecimals(4)
                setup["widget"].setValue(float(setup["value"]))
                setup["widget"].valueChanged.connect(partial(update, key))
                hbox.addWidget(setup["widget"], stretch=5)
                hbox.addWidget(QLabel("units"), stretch=1)
                vbox.addLayout(hbox)

            self.info = QLabel("")
            self.errors = QLabel("")
            self.animation = HomeAnimation(self.setup)

            vboxMain = QVBoxLayout()
            vboxMain.addWidget(self.animation)
            vboxMain.addWidget(self.info)
            vboxMain.addWidget(self.errors)
            vboxMain.addLayout(vbox)

            self.main = QWidget()
            self.setCentralWidget(self.main)
            self.main.setLayout(vboxMain)

            self.show()

    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    app.exec()
