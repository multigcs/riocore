#!/usr/bin/env python3
#
#

import os
import sys
import xml.etree.ElementTree as ET

from functools import partial

import hal
import linuxcnc

from PyQt5.QtCore import QRectF, QSize, QTimer, Qt, pyqtSignal
from PyQt5.QtGui import QBrush, QColor, QFont, QIcon, QLinearGradient, QPainter, QPen, QPixmap
from PyQt5.QtWidgets import (
    QApplication,
    QFileDialog,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QPlainTextEdit,
    QProgressBar,
    QProxyStyle,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QSlider,
    QStackedWidget,
    QStyle,
    QVBoxLayout,
    QWidget,
)
from qt5_graphics import Lcnc_3dGraphics

AXIS_NAMES = ["X", "Y", "Z", "A", "B", "C", "U", "V", "W"]

s = linuxcnc.stat()
c = linuxcnc.command()
e = linuxcnc.error_channel()
# h = hal.component(f"rg-{str(uuid.uuid4()).split('-')[0]}")
h = hal.component("pyvcp")

jog_mode = False


def ok_for_mdi():
    s.poll()
    return not s.estop and s.enabled and (s.homed.count(1) == s.joints) and (s.interp_state == linuxcnc.INTERP_IDLE)


class View3D(Lcnc_3dGraphics):
    def __init__(self):
        super().__init__()

    def report_gcode_error(self, arg1, arg2, arg3):
        print("ERROR1", arg1)
        print("ERROR2", arg2)
        print("ERROR3", arg3)
        print()


class GradientLabel(QLabel):
    def __init__(self, text=None, size=20, color1=None, color2=None, parent=None):
        super().__init__(text, parent)
        self.parent = parent
        self.text = text
        self.size = size
        if not color1:
            color1 = QColor("#206086")
        self.color1 = color1
        if not color2:
            color2 = QColor("#09405f")
        self.color2 = color2
        self.flag_clicked = False
        self.enabled = True

    clicked = pyqtSignal()

    def _groove_rect(self):
        return QRectF(0, 0, self.width(), self.height())

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        if not self.isEnabled():
            p.setOpacity(0.4)

        g = self._groove_rect()
        grad = QLinearGradient(g.topLeft(), g.bottomRight())
        if not self.enabled:
            if self.text:
                if self.text.lower() == "estop":
                    grad.setColorAt(0.0, QColor("#339933"))
                    grad.setColorAt(1.0, QColor("#66FF66"))
                else:
                    grad.setColorAt(0.0, QColor("#999999"))
                    grad.setColorAt(1.0, QColor("#ABABAB"))
        elif self.flag_clicked:
            grad.setColorAt(0.0, self.color1)
            grad.setColorAt(1.0, self.color2)
        else:
            grad.setColorAt(0.0, self.color2)
            grad.setColorAt(1.0, self.color1)

        # background
        p.setPen(Qt.NoPen)
        p.setBrush(QBrush(grad))
        # p.drawRoundedRect(g, 2, 2)
        p.drawRect(g)

        # text
        if self.text:
            font = QFont("Arial", self.size, weight=QFont.Bold)
            p.setFont(font)
            p.setPen(QPen(Qt.white, 1))
            p.drawText(QRectF(0, 0, self.width(), self.height()), Qt.AlignCenter, self.text)

    def minimumSizeHint(self):
        return QSize(40, 70)

    def mousePressEvent(self, event):
        self.clicked.emit()
        self.flag_clicked = True
        self.update()
        if self.text and self.text[0] in AXIS_NAMES and self.text[1] in {"+", "-"}:
            axis = AXIS_NAMES.index(self.text[0])
            speed = self.parent.jog_speed
            if self.text[1] == "-":
                speed *= -1
            c.mode(linuxcnc.MODE_MANUAL)
            if jog_mode:
                c.teleop_enable(0)
            else:
                c.teleop_enable(1)
            c.wait_complete()
            c.jog(linuxcnc.JOG_CONTINUOUS, jog_mode, axis, speed)
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        self.flag_clicked = False
        self.update()
        if self.text:
            if self.text.lower() == "estop":
                if self.enabled:
                    c.state(linuxcnc.STATE_ESTOP_RESET)
                else:
                    c.state(linuxcnc.STATE_ESTOP)
            elif self.text.lower() == "home":
                c.mode(linuxcnc.MODE_MANUAL)
                c.teleop_enable(0)
                c.wait_complete()
                c.home(-1)

            elif self.text.lower() == "enable":
                if self.enabled:
                    c.state(linuxcnc.STATE_OFF)
                else:
                    c.state(linuxcnc.STATE_ON)
            elif self.text[0] in AXIS_NAMES and self.text[1] in {"+", "-"}:
                axis = AXIS_NAMES.index(self.text[0])
                c.jog(linuxcnc.JOG_STOP, jog_mode, axis)
        super().mouseReleaseEvent(event)


class GradientDRO(QLabel):
    def __init__(self, text=None, color1=None, color2=None, parent=None):
        super().__init__(text, parent)
        self.text = text
        if not color1:
            color1 = QColor("#206086")
        self.color1 = color1
        if not color2:
            color2 = QColor("#09405f")
        self.color2 = color2
        self.values = {}

    def _groove_rect(self):
        return QRectF(0, 0, self.width(), self.height())

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        if not self.isEnabled():
            p.setOpacity(0.4)

        g = self._groove_rect()
        grad = QLinearGradient(g.topLeft(), g.bottomRight())
        grad.setColorAt(0.0, self.color1)
        grad.setColorAt(1.0, self.color2)

        # background
        p.setPen(Qt.NoPen)
        p.setBrush(QBrush(grad))
        p.drawRect(g)

        # text
        p.setPen(QPen(Qt.white, 1))

        if self.text:
            font = QFont("Arial", 16, weight=QFont.Bold)
            p.setFont(font)
            p.drawText(QRectF(0.0, 10.0, self.width(), 30.0), Qt.AlignCenter, self.text)

        font = QFont("Arial", 22, weight=QFont.Bold)
        p.setFont(font)
        pd = 60
        py = 60
        for name, values in self.values.items():
            p.drawText(QRectF(40, py, self.width() - 80, pd), Qt.AlignLeft, f"{name}")
            p.drawText(QRectF(40, py, self.width() - 80, pd), Qt.AlignRight, f"{values['pos']:0.3f}mm")
            py += pd

        font = QFont("Arial", 12)
        p.setFont(font)
        py = 60
        for name, values in self.values.items():
            p.drawText(QRectF(70, py, self.width() - 120, pd), Qt.AlignLeft, f"{'*' if values['homed'] else ''}")
            p.drawText(QRectF(80, py + 14, self.width() - 120, pd + 14), Qt.AlignLeft, f"{values['velocity']:0.1f}mm/s")
            py += pd


class GradientSlider(QSlider):
    def __init__(self, title=None, color1=None, color2=None, image=None, parent=None):
        super().__init__(Qt.Orientation.Horizontal, parent)
        self.parent = parent
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.pixmap = None
        self.title = title
        if image is not None:
            self.pixmap = QPixmap(image)
        if not color1:
            color1 = QColor("#206086")
        self.color1 = color1
        if not color2:
            color2 = QColor("#09405f")
        self.color2 = color2
        self.is_moving = False

    def _groove_rect(self):
        return QRectF(0, 0, self.width(), self.height())

    def _fraction(self):
        span = self.maximum() - self.minimum()
        return (self.sliderPosition() - self.minimum()) / span if span else 0.0

    def _value_at(self, pos):
        g = self._groove_rect()
        f = (pos.x() - g.left()) / max(g.width(), 1)
        f = min(1.0, max(0.0, f))
        return round(self.minimum() + f * (self.maximum() - self.minimum()))

    def minimumSizeHint(self):
        if self.pixmap:
            return QSize(120, 100)
        return QSize(120, 60)

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        if not self.isEnabled():
            p.setOpacity(0.4)

        g = self._groove_rect()
        grad = QLinearGradient(g.topLeft(), g.bottomRight())
        grad.setColorAt(0.0, self.color1)
        grad.setColorAt(1.0, self.color2)
        grad2 = QLinearGradient(g.topLeft(), g.topRight())
        grad2.setColorAt(0.0, QColor("#444545"))
        grad2.setColorAt(1.0, QColor("#ff4545"))

        # background
        p.setPen(Qt.NoPen)
        p.setBrush(QBrush(grad))
        p.drawRect(g)

        # slider
        f = self._fraction()
        g = QRectF(0, 0, self.width() * f, self.height())
        p.setBrush(QBrush(grad2))
        p.drawRect(g)

        # icon
        if self.pixmap is not None and self.pixmap.height():
            margin = 20
            pw = self.width() // 3 - margin
            ph = self.height() - margin
            ps = min(pw / self.pixmap.width(), ph / self.pixmap.height())

            npw = self.pixmap.width() * ps
            nph = self.pixmap.height() * ps
            irw = self.width() / 3
            irh = self.height()
            poffx = (irw - npw) / 2
            poffy = (irh - nph) / 2

            p.drawPixmap(int(poffx), int(poffy), int(self.pixmap.width() * ps), int(self.pixmap.height() * ps), self.pixmap)

        # text
        font = QFont("Arial", 20, weight=QFont.Bold)
        p.setFont(font)
        p.setPen(QPen(Qt.white, 1))
        text = f"{self._fraction() * 100:2.0f}%"
        p.drawText(QRectF(10, self.height() - 40, self.width() - 20, 40), Qt.AlignLeft, text)

        if self.title:
            p.setFont(QFont("Arial", 12))
            p.drawText(QRectF(self.width() / 3, 10.0, self.width() / 3 * 2, 30.0), Qt.AlignCenter, self.title)

        text = "400mm/s"
        p.drawText(QRectF(10, self.height() - 40, self.width() - 20, 40), Qt.AlignRight, text)
        p.drawLine(self.width() // 3, 10, self.width() // 3, self.height() - 10)

    # ---------- mouse: map click/drag directly to a value ----------
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.setSliderDown(True)  # emits sliderPressed
            self.setSliderPosition(self._value_at(event.pos()))
            event.accept()
        else:
            super().mousePressEvent(event)
        self.is_moving = True

    def mouseMoveEvent(self, event):
        if self.isSliderDown():
            self.setSliderPosition(self._value_at(event.pos()))  # sliderMoved / valueChanged
            event.accept()
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton and self.isSliderDown():
            self.setSliderDown(False)  # emits sliderReleased
            event.accept()
        else:
            super().mouseReleaseEvent(event)

        if self.title and self.title.split("-")[0].lower() == "rapid":
            c.rapidrate(self.value() / 100.0)
        elif self.title and self.title.split("-")[0].lower() == "feed":
            c.feedrate(self.value() / 100.0)
        elif self.title and self.title.split("-")[0].lower() == "spindle":
            c.spindleoverride(self.value() / 100.0, 0)
        elif self.title and self.title.split("-")[0].lower() == "jog":
            self.parent.jog_speed = self.value()

        self.is_moving = False


class ScreenJog(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        jogv = QVBoxLayout()
        jogv.setContentsMargins(0, 0, 0, 0)
        # jogv.setSpacing(0)
        self.setLayout(jogv)

        color1 = QColor("#151514")
        color2 = QColor("#15154f")

        jogh0 = QHBoxLayout()
        jogv.addLayout(jogh0, stretch=1)

        xp = GradientLabel("", color1=color1, color2=color2)
        jogh0.addWidget(xp, stretch=1)
        xp = GradientLabel("A+", parent=self.parent)
        jogh0.addWidget(xp, stretch=1)
        xp = GradientLabel("", color1=color1, color2=color2)
        jogh0.addWidget(xp, stretch=1)
        xp = GradientLabel("C+", parent=self.parent)
        jogh0.addWidget(xp, stretch=1)
        xp = GradientLabel("", color1=color1, color2=color2)
        jogh0.addWidget(xp, stretch=1)

        jogh1 = QHBoxLayout()
        jogv.addLayout(jogh1, stretch=1)

        xp = GradientLabel("", color1=color1, color2=color2)
        jogh1.addWidget(xp, stretch=1)
        xp = GradientLabel("A-", parent=self.parent)
        jogh1.addWidget(xp, stretch=1)
        xp = GradientLabel("", color1=color1, color2=color2)
        jogh1.addWidget(xp, stretch=1)
        xp = GradientLabel("C-", parent=self.parent)
        jogh1.addWidget(xp, stretch=1)
        xp = GradientLabel("", color1=color1, color2=color2)
        jogh1.addWidget(xp, stretch=1)

        jogh2 = QHBoxLayout()
        jogv.addLayout(jogh2, stretch=2)

        xp = GradientLabel("", color1=color1, color2=color2)
        jogh2.addWidget(xp, stretch=1)
        xp = GradientLabel("Y+", parent=self.parent)
        jogh2.addWidget(xp, stretch=1)
        xp = GradientLabel("Z+", parent=self.parent)
        jogh2.addWidget(xp, stretch=1)

        jogh3 = QHBoxLayout()
        jogv.addLayout(jogh3, stretch=2)

        xp = GradientLabel("X-", parent=self.parent)
        jogh3.addWidget(xp, stretch=1)
        xp = GradientLabel("HOME")
        jogh3.addWidget(xp, stretch=1)
        xp = GradientLabel("X+", parent=self.parent)
        jogh3.addWidget(xp, stretch=1)

        jogh4 = QHBoxLayout()
        jogv.addLayout(jogh4, stretch=2)

        xp = GradientLabel("", color1=color1, color2=color2)
        jogh4.addWidget(xp, stretch=1)
        xp = GradientLabel("Y-", parent=self.parent)
        jogh4.addWidget(xp, stretch=1)
        xp = GradientLabel("Z-", parent=self.parent)
        jogh4.addWidget(xp, stretch=1)

        slider_jog = GradientSlider(title="Jog-Speed", parent=self.parent)
        slider_jog.setRange(0, 100)
        slider_jog.setValue(50)
        jogv.addWidget(slider_jog, stretch=1)


class ScreenMdi(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        self.setLayout(layout)

        self.history = QListWidget()
        self.history.setStyleSheet("""
            QListWidget {
                background-color: #2b2b2b;
                color: #ffffff;
                font-family: 'Consolas', 'Courier New', monospace;
                font-size: 14pt;
            }
            QScrollBar:vertical {
                background-color: qlineargradient(x1: 0, y1: 0, x2: 1, xy: 1, stop: 0 #78a023, stop: 1 #9fc31b);
                width: 36px;
            }
        """)
        self.history.addItem(QListWidgetItem("G0 X0 Y0"))
        self.history.addItem(QListWidgetItem("G0 X10 Y10"))
        self.history.addItem(QListWidgetItem("G0 X0 Y10"))
        self.history.addItem(QListWidgetItem("G0 X0 Y10"))
        self.history.addItem(QListWidgetItem("G0 X0 Y10"))
        self.history.addItem(QListWidgetItem("G0 X0 Y0"))
        self.history.addItem(QListWidgetItem("G0 X10 Y10"))
        self.history.addItem(QListWidgetItem("G0 X0 Y10"))
        self.history.addItem(QListWidgetItem("G0 X0 Y10"))
        self.history.addItem(QListWidgetItem("G0 X0 Y10"))
        self.history.addItem(QListWidgetItem("G0 X0 Y10"))
        self.history.addItem(QListWidgetItem("G0 X0 Y10"))
        self.history.addItem(QListWidgetItem("G0 X0 Y0"))
        self.history.addItem(QListWidgetItem("G0 X10 Y10"))
        self.history.addItem(QListWidgetItem("G0 X0 Y10"))
        self.history.addItem(QListWidgetItem("G0 X0 Y10"))
        self.history.addItem(QListWidgetItem("G0 X0 Y10"))
        self.history.addItem(QListWidgetItem("G0 X0 Y0"))
        self.history.addItem(QListWidgetItem("G0 X10 Y10"))
        self.history.addItem(QListWidgetItem("G0 X0 Y10"))
        self.history.addItem(QListWidgetItem("G0 X0 Y0"))
        self.history.addItem(QListWidgetItem("G0 X10 Y10"))
        self.history.addItem(QListWidgetItem("G0 X0 Y10"))
        self.history.addItem(QListWidgetItem("G0 X0 Y10"))
        self.history.addItem(QListWidgetItem("G0 X0 Y10"))
        layout.addWidget(self.history)

        self.cmd = QLineEdit()
        self.cmd.setStyleSheet("""
            background-color: #5b5b5b;
            color: #ffffff;
            font-family: 'Consolas', 'Courier New', monospace;
            font-size: 14pt;
        """)
        layout.addWidget(self.cmd)


class ScreenProg(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        self.setLayout(layout)


class SliderProxyStyle(QProxyStyle):
    def pixelMetric(self, metric, option, widget):
        if metric in {QStyle.PM_SliderThickness, QStyle.PM_SliderLength}:
            return 40
        return super().pixelMetric(metric, option, widget)


class ScreenVcpTab(QWidget):
    def __init__(self, tab, halpins_in):
        super().__init__()
        # self.setStyleSheet("background-color: qlineargradient(x1: 0, y1: 0, x2: 1, xy: 1, stop: 0 #151514, stop: 1 #15154f); color : white;")
        # self.setStyleSheet("background-color: qlineargradient(x1: 0, y1: 0, x2: 1, xy: 1, stop: 0 #78a023, stop: 1 #9fc31b); color : white;")
        self.setStyleSheet("""
            background-color: #9fc31b;
            color : black;
            font-size: 22px;
        """)

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        self.setLayout(layout)

        def next_element(element, layout, prefix=""):
            for child in element:
                # print(prefix, child.tag, child.attrib)
                if child.tag == "label":
                    text = ""
                    anchor = "c"
                    width = ""
                    for child2 in child:
                        if child2.tag == "format":
                            vformat = child2.text.strip('"')
                        elif child2.tag == "anchor":
                            anchor = child2.text.strip('"')
                        elif child2.tag == "text":
                            text = child2.text.strip('"')
                        elif child2.tag == "width":
                            width = child2.text.strip('"')
                    label = QLabel(text)
                    if width:
                        label.setFixedWidth(int(width) * 15)
                    if anchor == "e":
                        label.setAlignment(Qt.AlignRight)
                    elif anchor == "w":
                        label.setAlignment(Qt.AlignLeft)
                    elif anchor == "c":
                        label.setAlignment(Qt.AlignCenter)
                    label.setContentsMargins(0, 0, 0, 0)
                    layout.addWidget(label)
                elif child.tag in {"led", "rectled"}:
                    label = QLabel("[O]")
                    label.setContentsMargins(0, 0, 0, 0)
                    layout.addWidget(label)
                    for child2 in child:
                        if child2.tag == "halpin":
                            halpin = child2.text.strip('"')
                            h.newpin(f"{halpin}", hal.HAL_BIT, hal.HAL_IN)
                            halpins_in[halpin] = (child.tag, label)
                elif child.tag in {"number", "s32", "u32"}:
                    anchor = "c"
                    vformat = "0.0f"
                    for child2 in child:
                        if child2.tag == "format":
                            vformat = child2.text.strip('"')
                        elif child2.tag == "anchor":
                            anchor = child2.text.strip('"')
                    label = QLabel("<NUMBER>")
                    if anchor == "e":
                        label.setAlignment(Qt.AlignRight)
                    elif anchor == "w":
                        label.setAlignment(Qt.AlignLeft)
                    elif anchor == "c":
                        label.setAlignment(Qt.AlignCenter)
                    label.setContentsMargins(0, 0, 0, 0)
                    layout.addWidget(label)
                    for child2 in child:
                        if child2.tag == "halpin":
                            halpin = child2.text.strip('"')
                            if child.tag in {"s32"}:
                                h.newpin(f"{halpin}", hal.HAL_S32, hal.HAL_IN)
                            elif child.tag in {"u32"}:
                                h.newpin(f"{halpin}", hal.HAL_U32, hal.HAL_IN)
                            else:
                                h.newpin(f"{halpin}", hal.HAL_FLOAT, hal.HAL_IN)
                            halpins_in[halpin] = (child.tag, label, vformat)
                elif child.tag == "multilabel":
                    label = QLabel("<MULTILABEL>")
                    label.setAlignment(Qt.AlignCenter)
                    label.setContentsMargins(0, 0, 0, 0)
                    layout.addWidget(label)
                    legends = []
                    for child2 in child:
                        if child2.tag == "legends":
                            for part in child2.text.strip("[]").split(","):
                                legends.append(part.strip("' "))
                    for child2 in child:
                        if child2.tag == "halpin":
                            halpin = child2.text.strip('"')
                            for legend_n, legend_name in enumerate(legends):
                                h.newpin(f"{halpin}.legend{legend_n}", hal.HAL_BIT, hal.HAL_IN)
                            halpins_in[halpin] = (child.tag, label, legends)

                elif child.tag == "bar":
                    vmin = "0"
                    vmax = "100"
                    # interval = "1"
                    anchor = "c"
                    vformat = "0.0f"
                    for child2 in child:
                        if child2.tag == "format":
                            vformat = child2.text.strip('"')
                        elif child2.tag == "min":
                            vmin = child2.text.strip('"')
                        elif child2.tag == "max":
                            vmax = child2.text.strip('"')
                        # elif child2.tag == "interval":
                        #    interval = child2.text.strip('"')
                    label = QProgressBar()
                    label.setContentsMargins(0, 0, 0, 0)
                    label.setMinimum(int(vmin) * 10)
                    label.setMaximum(int(vmax) * 10)
                    label.setValue(50 * 10)
                    layout.addWidget(label)
                    for child2 in child:
                        if child2.tag == "halpin":
                            halpin = child2.text.strip('"')
                            h.newpin(f"{halpin}", hal.HAL_FLOAT, hal.HAL_IN)
                            halpins_in[halpin] = (child.tag, label)

                elif child.tag == "scale":
                    vmin = "0"
                    vmax = "100"
                    # resolution = "1.0"
                    initval = "0"
                    for child2 in child:
                        if child2.tag == "min_":
                            vmin = child2.text.strip('"')
                        elif child2.tag == "max_":
                            vmax = child2.text.strip('"')
                        # elif child2.tag == "resolution":
                        #    resolution = child2.text.strip('"')
                        elif child2.tag == "initval":
                            initval = child2.text.strip('"')
                    label = QSlider(Qt.Orientation.Horizontal)
                    label.setStyle(SliderProxyStyle(label.style()))
                    label.setContentsMargins(0, 0, 0, 0)
                    label.setMinimum(int(vmin) * 10)
                    label.setMaximum(int(vmax) * 10)
                    label.setValue(int(initval) * 10)
                    layout.addWidget(label)
                    for child2 in child:
                        if child2.tag == "halpin":
                            halpin = child2.text.strip('"')
                            h.newpin(f"{halpin}-i", hal.HAL_S32, hal.HAL_OUT)
                            h.newpin(f"{halpin}-f", hal.HAL_FLOAT, hal.HAL_OUT)

                            def change(halpin, val):
                                h[f"{halpin}-i"] = int(val / 10)
                                h[f"{halpin}-f"] = val / 10

                            label.valueChanged.connect(partial(change, halpin))

                elif child.tag == "checkbutton":
                    checkbox = QPushButton()
                    checkbox.setContentsMargins(0, 0, 0, 0)
                    checkbox.setCheckable(True)
                    layout.addWidget(checkbox)
                    for child2 in child:
                        if child2.tag == "halpin":
                            halpin = child2.text.strip('"')
                            h.newpin(f"{halpin}", hal.HAL_BIT, hal.HAL_OUT)

                            def change(halpin, val):
                                h[f"{halpin}"] = val
                                if val:
                                    checkbox.setStyleSheet("background-color : red")
                                else:
                                    checkbox.setStyleSheet("background-color : lightblue")

                            checkbox.clicked.connect(partial(change, halpin))
                    checkbox.setStyleSheet("background-color : lightblue")

                elif child.tag == "button":
                    text = ""
                    for child2 in child:
                        if child2.tag == "text":
                            text = child2.text.strip('"')
                    button = QPushButton(text)
                    button.setContentsMargins(0, 0, 0, 0)
                    layout.addWidget(button)

                    for child2 in child:
                        if child2.tag == "halpin":
                            halpin = child2.text.strip('"')
                            h.newpin(f"{halpin}", hal.HAL_BIT, hal.HAL_OUT)

                            def change(halpin, val):
                                h[f"{halpin}"] = val

                            button.pressed.connect(partial(change, halpin, True))
                            button.released.connect(partial(change, halpin, False))

                elif child.tag == "labelframe":
                    frame = QGroupBox()
                    vbox = QVBoxLayout()
                    vbox.setContentsMargins(0, 0, 0, 0)
                    vbox.setSpacing(0)
                    frame.setLayout(vbox)
                    frame.setTitle(child.attrib["text"])
                    layout.addWidget(frame)
                    next_element(child, vbox, prefix=" " + prefix)
                elif child.tag == "hbox":
                    hbox = QHBoxLayout()
                    hbox.setContentsMargins(0, 0, 0, 0)
                    hbox.setSpacing(0)
                    layout.addLayout(hbox)
                    next_element(child, hbox, prefix=" " + prefix)
                elif child.tag == "vbox":
                    vbox = QVBoxLayout()
                    vbox.setContentsMargins(0, 0, 0, 0)
                    vbox.setSpacing(0)
                    layout.addLayout(vbox)
                    next_element(child, vbox, prefix=" " + prefix)

                elif child.tag in {"boxanchor", "boxfill", "boxexpand", "font", "relief", ""}:
                    pass

                else:
                    print("missing:", child.tag)

        next_element(tab, layout)
        layout.addWidget(QLabel(""), stretch=1)


class ScreenOverwrites(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        # layout.setSpacing(0)
        self.setLayout(layout)

        self.slider_feed = GradientSlider(title="Feed-Overwrite", image="touchprobe.png")
        self.slider_feed.setRange(0, 100)
        layout.addWidget(self.slider_feed, stretch=2)

        self.slider_rapid = GradientSlider(title="Rapid-Overwrite", image="jogwheel.png")
        self.slider_rapid.setRange(0, 100)
        layout.addWidget(self.slider_rapid, stretch=2)

        self.slider_spindle = GradientSlider(title="Spindle-Overwrite", image="valve.png")
        self.slider_spindle.setRange(0, 100)
        layout.addWidget(self.slider_spindle, stretch=2)


class ScreenDro(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        self.setLayout(layout)
        self.dro = GradientDRO("Position", color1=QColor("#78a023"), color2=QColor("#9fc31b"))
        layout.addWidget(self.dro, stretch=3)


class ScreenNgc(QWidget):
    def __init__(self, parent):
        super().__init__()
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        self.setLayout(layout)

        hbox = QHBoxLayout()
        hbox.setContentsMargins(0, 0, 0, 0)
        hbox.setSpacing(0)
        layout.addLayout(hbox, stretch=5)

        btn_open = QPushButton(QIcon("open.png"), "OPEN")
        btn_open.setStyleSheet("background-color: qlineargradient(x1: 0, y1: 0, x2: 1, xy: 1, stop: 0 #78a023, stop: 1 #9fc31b); height: 50px;")
        btn_open.clicked.connect(parent.load_ngc)
        hbox.addWidget(btn_open, stretch=0)

        def prog_mode(mode):
            s.poll()
            if s.task_mode != linuxcnc.MODE_AUTO:
                c.mode(linuxcnc.MODE_AUTO)
            if mode == "RUN":
                c.auto(linuxcnc.AUTO_RUN, 1)
            elif mode == "STEP":
                c.auto(linuxcnc.AUTO_STEP)
            elif mode == "PAUSE":
                if s.interp_state != linuxcnc.INTERP_IDLE:
                    c.auto(linuxcnc.AUTO_PAUSE)
            elif mode == "RESUME":
                c.auto(linuxcnc.AUTO_RESUME)
            elif mode == "STOP":
                c.abort()

        btn_run = QPushButton(QIcon("play.png"), "RUN")
        btn_run.setStyleSheet("background-color: qlineargradient(x1: 0, y1: 0, x2: 1, xy: 1, stop: 0 #78a023, stop: 1 #9fc31b); height: 50px;")
        btn_run.clicked.connect(partial(prog_mode, "RUN"))
        hbox.addWidget(btn_run, stretch=0)

        btn_pause = QPushButton(QIcon("pause.png"), "PAUSE")
        btn_pause.setStyleSheet("background-color: qlineargradient(x1: 0, y1: 0, x2: 1, xy: 1, stop: 0 #78a023, stop: 1 #9fc31b); height: 50px;")
        btn_pause.clicked.connect(partial(prog_mode, "PAUSE"))
        hbox.addWidget(btn_pause, stretch=0)

        btn_step = QPushButton(QIcon("step.png"), "STEP")
        btn_step.setStyleSheet("background-color: qlineargradient(x1: 0, y1: 0, x2: 1, xy: 1, stop: 0 #78a023, stop: 1 #9fc31b); height: 50px;")
        btn_step.clicked.connect(partial(prog_mode, "STEP"))
        hbox.addWidget(btn_step, stretch=0)

        btn_stop = QPushButton(QIcon("stop.png"), "STOP")
        btn_stop.setStyleSheet("background-color: qlineargradient(x1: 0, y1: 0, x2: 1, xy: 1, stop: 0 #78a023, stop: 1 #9fc31b); height: 50px;")
        btn_stop.clicked.connect(partial(prog_mode, "STOP"))
        hbox.addWidget(btn_stop, stretch=0)

        self.editor = QPlainTextEdit()
        self.editor.setStyleSheet("""
            QPlainTextEdit {
                background-color: #2b2b2b;
                color: #ffffff;
                font-family: 'Consolas', 'Courier New', monospace;
                font-size: 12pt;
            }
            QScrollBar:vertical {
                background-color: qlineargradient(x1: 0, y1: 0, x2: 1, xy: 1, stop: 0 #78a023, stop: 1 #9fc31b);
                width: 36px;
            }
        """)
        layout.addWidget(self.editor, stretch=5)


class PyVCP:
    def __init__(self, layout, xml_file):
        self.layout = layout
        self.tabnames = []
        self.halpins_in = {}
        if xml_file:
            tree = ET.parse(xml_file)
            root = tree.getroot()
            for tabs in root:
                tab_n = 0
                for tab in tabs:
                    if tab.tag == "names":
                        for part in tab.text.strip("[]").split(","):
                            self.tabnames.append(part.strip("' "))
                    else:
                        self.screen_status = ScreenVcpTab(tab, self.halpins_in)
                        scroll = QScrollArea()
                        scroll.setStyleSheet("""
                            QScrollBar:vertical {
                                background-color: qlineargradient(x1: 0, y1: 0, x2: 1, xy: 1, stop: 0 #78a023, stop: 1 #9fc31b);
                                width: 36px;
                            }
                        """)
                        scroll.setWidget(self.screen_status)
                        scroll.setWidgetResizable(True)
                        self.layout.addWidget(scroll)
                        tab_n += 1

    def update(self):
        for pin, data in self.halpins_in.items():
            if data[0] in {"led", "rectled"}:
                val = h[f"{pin}"]
                if val:
                    data[1].setText("X")
                else:
                    data[1].setText("O")
            elif data[0] == "bar":
                val = h[f"{pin}"]
                data[1].setValue(int(val * 10))

            elif data[0] in {"number", "s32", "u32"}:
                val = h[f"{pin}"]
                vformat = data[2]
                if vformat == "d":
                    vformat = "0.0f"
                data[1].setText(f"{{value:{vformat}}}".format(value=val))
            elif data[0] == "multilabel":
                for legend_n, legend_name in enumerate(data[2]):
                    val = h[f"{pin}.legend{legend_n}"]
                    if val is True:
                        data[1].setText(legend_name)
            else:
                print("missing:", pin, data, val)

    def buttons(self, layout):
        for tab_n, tabname in enumerate(self.tabnames):
            btn_status = GradientLabel(tabname, 10)
            btn_status.clicked.connect(partial(self.layout.setCurrentIndex, tab_n))
            layout.addWidget(btn_status, stretch=1)


class MainWindow(QMainWindow):
    last_offsets = []
    ngc_file = ""
    jog_speed = 40

    def __init__(self):
        super().__init__()
        self.setWindowTitle("RIO-Next")
        self.resize(1200, 1920)
        # self.resize(800, 1080)

        mw = QWidget()
        self.setStyleSheet("background-color: qlineargradient(x1: 0, y1: 0, x2: 1, xy: 1, stop: 0 #151514, stop: 1 #15154f);")
        main_layout = QVBoxLayout(mw)
        main_layout.setContentsMargins(0, 0, 0, 0)
        self.setCentralWidget(mw)

        title_layout = QHBoxLayout()
        title_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addLayout(title_layout, stretch=0)

        top_layout = QHBoxLayout()
        top_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addLayout(top_layout, stretch=1)

        center1_layout = QHBoxLayout()
        center1_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addLayout(center1_layout, stretch=1)
        center1l_layout = QVBoxLayout()
        center1l_layout.setContentsMargins(0, 0, 0, 0)
        center1_layout.addLayout(center1l_layout, stretch=1)
        center1r_layout = QVBoxLayout()
        center1r_layout.setContentsMargins(0, 0, 0, 0)
        center1_layout.addLayout(center1r_layout, stretch=1)

        center2_layout = QHBoxLayout()
        center2_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addLayout(center2_layout, stretch=2)
        center2l_layout = QVBoxLayout()
        center2l_layout.setContentsMargins(0, 0, 0, 0)
        center2_layout.addLayout(center2l_layout, stretch=1)
        center2r_layout = QVBoxLayout()
        center2r_layout.setContentsMargins(0, 0, 0, 0)
        center2_layout.addLayout(center2r_layout, stretch=1)

        bottom_layout = QHBoxLayout()
        bottom_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addLayout(bottom_layout, stretch=0)

        bottoml_layout = QHBoxLayout()
        bottoml_layout.setContentsMargins(0, 0, 0, 0)
        bottom_layout.addLayout(bottoml_layout, stretch=1)

        bottomr_layout = QHBoxLayout()
        bottomr_layout.setContentsMargins(0, 0, 0, 0)
        bottom_layout.addLayout(bottomr_layout, stretch=1)

        self.estop = GradientLabel("ESTOP", size=14, color1=QColor("#993333"), color2=QColor("#FF6666"))
        title_layout.addWidget(self.estop, stretch=1)
        title = GradientLabel("LinuxCNC - RIO")
        title_layout.addWidget(title, stretch=9)
        self.enable = GradientLabel("ENABLE", size=14, color1=QColor("#339933"), color2=QColor("#66FF66"))
        title_layout.addWidget(self.enable, stretch=1)

        self.glview = View3D()
        top_layout.addWidget(self.glview, stretch=1)

        self.center1l_stack = QStackedWidget()
        center1l_layout.addWidget(self.center1l_stack, stretch=1)
        self.screen_overwrites = ScreenOverwrites()
        self.center1l_stack.addWidget(self.screen_overwrites)

        self.center1r_stack = QStackedWidget()
        center1r_layout.addWidget(self.center1r_stack, stretch=1)
        self.screen_dro = ScreenDro()
        self.center1r_stack.addWidget(self.screen_dro)

        self.center2l_stack = QStackedWidget()
        center2l_layout.addWidget(self.center2l_stack, stretch=1)
        self.screen_jog = ScreenJog(self)
        self.center2l_stack.addWidget(self.screen_jog)
        self.screen_mdi = ScreenMdi()
        self.center2l_stack.addWidget(self.screen_mdi)
        self.screen_prog = ScreenNgc(self)
        self.center2l_stack.addWidget(self.screen_prog)

        self.center2r_stack = QStackedWidget()
        center2r_layout.addWidget(self.center2r_stack, stretch=1)

        s.poll()
        self.inifile = linuxcnc.ini(s.ini_filename)
        xml_file = self.inifile.find("DISPLAY", "PYVCP")
        # self.joints = int(self.inifile.find("KINS", "JOINTS"))

        self.pyvcp = None
        if xml_file:
            self.pyvcp = PyVCP(self.center2r_stack, xml_file)

        btn_jog = GradientLabel("JOG", 14)
        btn_jog.clicked.connect(partial(self.center2l_stack.setCurrentIndex, 0))
        bottoml_layout.addWidget(btn_jog, stretch=1)

        btn_mdi = GradientLabel("MDI", 14)
        btn_mdi.clicked.connect(partial(self.center2l_stack.setCurrentIndex, 1))
        bottoml_layout.addWidget(btn_mdi, stretch=1)

        def open_prog(idx):
            self.center2l_stack.setCurrentIndex(idx)
            if not os.path.isfile(self.ngc_file):
                self.load_ngc()

        btn_prog = GradientLabel("PROG", 14)
        btn_prog.clicked.connect(partial(open_prog, 2))
        bottoml_layout.addWidget(btn_prog, stretch=1)

        glabel2 = GradientLabel("")
        bottoml_layout.addWidget(glabel2, stretch=1)
        glabel2 = GradientLabel("")
        bottoml_layout.addWidget(glabel2, stretch=1)
        glabel2 = GradientLabel("")
        bottoml_layout.addWidget(glabel2, stretch=1)

        if self.pyvcp:
            self.pyvcp.buttons(bottomr_layout)

        self.postgui()

        self.timer = QTimer()
        self.timer.timeout.connect(self.runTimer)
        self.timer.start(100)

    def postgui(self):
        for filename in self.inifile.findall("HAL", "POSTGUI_HALFILE") or []:
            ini_dir = os.path.dirname(s.ini_filename)
            haltcl = ["haltcl", "-i", ini_dir, "-f", str(filename)]
            if filename.split(".")[-1] == "tcl":
                haltcl = ["haltcl", "-i", ini_dir, str(filename)]
            ret = os.spawnvp(os.P_WAIT, "halcmd", haltcl)
            if ret != 0:
                raise SystemExit(ret)

    def load_ngc(self):
        file_dialog = QFileDialog(self)
        name = file_dialog.getOpenFileName(
            self,
            "Load a gCode file",
            "./",
            "gCode (*.ngc)",
        )
        if name[0]:
            self.ngc_file = name[0]
            if os.path.isfile(self.ngc_file):
                self.glview.load(self.ngc_file)
                self.screen_prog.editor.setPlainText(open(self.ngc_file, "r").read())
                c.program_open(self.ngc_file)

    def runTimer(self):
        s.poll()
        if not self.screen_overwrites.slider_rapid.is_moving:
            self.screen_overwrites.slider_rapid.setValue(int(s.rapidrate * 100.0))
        if not self.screen_overwrites.slider_feed.is_moving:
            self.screen_overwrites.slider_feed.setValue(int(s.feedrate * 100.0))
        if not self.screen_overwrites.slider_spindle.is_moving:
            self.screen_overwrites.slider_spindle.setValue(int(s.spindle[0]["override"] * 100.0))

        values = {}
        if all(s.homed[: s.joints]):
            for n, pos in enumerate(s.position[: s.joints]):
                values[AXIS_NAMES[n]] = {
                    "pos": pos - s.g92_offset[n],
                    "velocity": s.axis[n]["velocity"],
                    "homed": s.homed[n],
                }
        else:
            for n, pos in enumerate(s.joint_position[: s.joints]):
                values[str(n)] = {
                    "pos": pos,
                    "velocity": s.joint[n]["velocity"],
                    "homed": s.homed[n],
                }

        if self.last_offsets != s.g92_offset:
            self.last_offsets = s.g92_offset
            if os.path.isfile(self.ngc_file):
                print("glview: autoreload")
                self.glview.load(self.ngc_file)

        if self.screen_dro.dro.values != values:
            self.screen_dro.dro.values = values
            self.screen_dro.dro.update()

        if self.estop.enabled != s.estop:
            self.estop.enabled = s.estop
            self.estop.update()

        if self.enable.enabled != s.enabled:
            self.enable.enabled = s.enabled
            self.enable.update()

        if self.pyvcp:
            self.pyvcp.update()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    h.ready()
    window.show()
    sys.exit(app.exec_())
