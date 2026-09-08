#!/usr/bin/env python3
#
#

import argparse
import glob
import os
import sys
import xml.etree.ElementTree as ET

from datetime import datetime
from functools import partial

import cv2
import gcode
import hal
import linuxcnc
import numpy as np

from PyQt5 import QtSvg
from PyQt5.QtCore import QPointF, QRectF, QSize, QThread, QTimer, Qt, pyqtSignal
from PyQt5.QtGui import QBrush, QColor, QFont, QIcon, QImage, QLinearGradient, QPainter, QPen, QPixmap, QRadialGradient
from PyQt5.QtWidgets import (
    QAction,
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
    QSpacerItem,
    QStackedWidget,
    QStyle,
    QVBoxLayout,
    QWidget,
    QWidgetItem,
)
from qt5_graphics import Lcnc_3dGraphics

stylesheet = """
    QWidget {
        background-color: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1, stop: 0 #252524, stop: 1 #25256f);
        color: #ffffff;
        font-size: 14px;
        margin: 0px 0px 0px 0px;
    }

    QWidget#main {
        background-color: #454545;
        margin: 0px 0px 0px 0px;
    }

    QScrollBar:vertical {
        border: 2px solid white;
        width: 46px;
        margin: 52px 1px 52px 1px;
    }
    QScrollBar::handle:vertical {
        border: 2px solid white;
        min-height: 50px;
    }
    QScrollBar::sub-line:vertical {
        border: 2px solid white;
        height: 50px;
        subcontrol-position: top;
        subcontrol-origin: margin;
    }
    QScrollBar::add-line:vertical {
        border: 2px solid white;
        height: 50px;
        subcontrol-position: bottom;
        subcontrol-origin: margin;
    }

    QLineEdit {
        background-color: #5b5b5b;
        color: #ffffff;
        font-family: 'Consolas', 'Courier New', monospace;
        font-size: 24px;
    }
    QListWidget {
        background-color: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1, stop: 0 #206086, stop: 1 #09405f);
        color: #ffffff;
        font-family: 'Consolas', 'Courier New', monospace;
        font-size: 24px;
    }

    QLabel {
        color: #ffffff;
        font-weight: bold;
        font-size: 21px;
    }

    QLabel#estop {
        background-color: green;
        color: #ffffff;
        font-weight: bold;
        font-size: 16px;
    }
    QLabel#enable {
        background-color: green;
        color: #ffffff;
        font-weight: bold;
        font-size: 16px;
    }
    QLabel#exit {
        background-color: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1, stop: 0 #f06086, stop: 1 #f9405f);
        color: #ffffff;
        font-weight: bold;
        font-size: 16px;
    }

    QLabel#vcp_label {
        font-size: 21px;
    }
    QPushButton#vcp_button {
        font-size: 21px;
    }
    QLabel#vcp_number {
        font-size: 21px;
    }
    QGroupBox#vcp_labelframe {
        font-size: 21px;
        margin: 16px 0px 0px 0px;
    }

"""
"""
QLabel#vcp_label
QLabel#vcp_number
QLabel#vcp_multilabel
QProgressBar#vcp_bar
QSlider#vcp_scale
QPushButton#vcp_checkbutton
QPushButton#vcp_button
QGroupBox#vcp_labelframe
LED#vcp_led
"""

AXIS_NAMES = ["X", "Y", "Z", "A", "B", "C", "U", "V", "W"]

s = linuxcnc.stat()
s.poll()
c = linuxcnc.command()
e = linuxcnc.error_channel()
h_vcp = hal.component("pyvcp")
h_next = hal.component("next")

for axis in ("x", "y", "z"):
    h_next.newpin(f"axis.{axis}.jog-counts", hal.HAL_S32, hal.HAL_OUT)
    h_next.newpin(f"axis.{axis}.jog-scale", hal.HAL_FLOAT, hal.HAL_IN)
    h_next.newpin(f"axis.{axis}.cal", hal.HAL_FLOAT, hal.HAL_IN)


jog_mode = False


def ok_for_mdi():
    s.poll()
    return not s.estop and s.enabled and (s.homed.count(1) == s.joints) and (s.interp_state == linuxcnc.INTERP_IDLE)


def do_homing(axis=-1):
    c.mode(linuxcnc.MODE_MANUAL)
    c.teleop_enable(0)
    c.wait_complete()
    c.home(axis)


def cleanLayout(layout):
    for i in reversed(range(layout.count())):
        item = layout.itemAt(i)
        if isinstance(item, QWidgetItem):
            item.widget().close()
        elif isinstance(item, QSpacerItem):
            pass
        elif item is not None:
            cleanLayout(item.layout())
        layout.removeItem(item)


class View3D(Lcnc_3dGraphics):
    errortext = None
    error_widget = None

    def __init__(self):
        super().__init__()

    def load(self, filename, error_widget=None):
        self.errortext = None
        self.error_widget = error_widget
        print("error-widget", error_widget)
        super().load(filename)

    def report_gcode_error(self, result, seq, filename):
        error_str = gcode.strerror(result)
        errortext = "G-Code error in " + os.path.basename(filename) + "\n" + "Near line " + str(seq) + " of\n" + filename + "\n" + error_str + "\n"
        print("gcode-error", errortext)
        print("error-widget", self.error_widget)
        self.errortext = errortext
        if self.error_widget:
            self.error_widget.color1 = QColor("#ff6086")
            self.error_widget.color2 = QColor("#ff2036")
            self.error_widget.setError(self.errortext)


class GradientFileEntry(QLabel):
    def __init__(self, filename, objectName=None):
        super().__init__("", objectName=objectName)
        self.filename = filename
        self.error = ""
        self.flag_clicked = False
        self.enabled = None

    clicked = pyqtSignal()

    def setError(self, error):
        self.error = error
        self.update()

    def _groove_rect(self):
        return QRectF(0, 0, self.width(), self.height())

    def paintEvent(self, event):
        super().paintEvent(event)

        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        if not self.isEnabled():
            p.setOpacity(0.4)

        # text
        title = os.path.basename(self.filename)
        font = QFont("Arial", 20, weight=QFont.Bold)
        p.setFont(font)
        p.setPen(QPen(Qt.white, 1))
        p.drawText(QRectF(10, 10, self.width(), 40), Qt.AlignLeft, title)

        font = QFont("Arial", 14)
        p.setFont(font)
        p.setPen(QPen(Qt.white, 1))

        if self.error:
            p.drawText(QRectF(30, 60, self.width(), self.height() - 40), Qt.AlignLeft, self.error)
        else:
            size = os.path.getsize(self.filename) / 1024
            ctime = datetime.fromtimestamp(os.path.getctime(self.filename)).strftime("%H:%M %d.%m.%y")
            mtime = datetime.fromtimestamp(os.path.getmtime(self.filename)).strftime("%H:%M %d.%m.%y")
            p.drawText(QRectF(self.width() - 320, 10, 310, 30), Qt.AlignRight, f"Size: {size:0.2f}kb")
            p.drawText(QRectF(self.width() - 320, 10 + 30 * 1, 310, 30), Qt.AlignRight, f"cTime: {ctime}")
            p.drawText(QRectF(self.width() - 320, 10 + 30 * 2, 310, 30), Qt.AlignRight, f"mTime: {mtime}")
            p.drawText(QRectF(10, self.height() - 35, self.width(), 30), Qt.AlignLeft, f"Filename: {self.filename}")

    def minimumSizeHint(self):
        return QSize(450, 200)

    def mousePressEvent(self, event):
        self.clicked.emit()
        self.flag_clicked = True
        self.update()
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        self.flag_clicked = False
        self.update()
        super().mouseReleaseEvent(event)


class LED(QPushButton):
    def __init__(self, ltype=None, on_color=None, off_color=None, objectName=None):
        super().__init__("", objectName=objectName)
        self.setCheckable(True)
        self.ltype = ltype
        self.on_color = on_color
        self.off_color = off_color
        self.on = False

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        if not self.isEnabled():
            p.setOpacity(0.4)

        center = QPointF(self.width() / 2, self.height() / 2)
        rad = min(self.width(), self.height()) / 2
        grad = QRadialGradient(center, rad)
        if self.on:
            if self.on_color:
                grad.setColorAt(0, self.on_color)
            else:
                grad.setColorAt(0, QColor(255, 10, 10))
        elif self.off_color:
            grad.setColorAt(0, self.off_color)
        else:
            grad.setColorAt(0, QColor(0, 0, 0))
        grad.setColorAt(1, QColor(0, 0, 0))

        p.setPen(Qt.NoPen)
        p.setBrush(QBrush(grad))
        if self.ltype == "rectled":
            p.drawRect(QRectF(self.width() / 2 - rad, self.height() / 2 - rad, rad * 2, rad * 2))
        else:
            p.drawEllipse(center, rad, rad)


class GradientLabel(QLabel):
    clicked = pyqtSignal()

    def __init__(self, text=None, parent=None, ctype=None, objectName=None):
        super().__init__(text, parent, objectName=objectName)
        self.setAlignment(Qt.AlignCenter)
        self.parent = parent
        self.ctype = ctype
        self.text = text
        self.flag_clicked = False
        self.enabled = None

    def setText(self, text):
        self.text = text
        super().setText(text)

    def mousePressEvent(self, event):
        self.clicked.emit()
        self.flag_clicked = True
        self.update()
        if self.text and len(self.text) == 2 and self.text[0] in AXIS_NAMES and self.text[1] in {"+", "-"}:
            axis = AXIS_NAMES.index(self.text[0])
            speed = self.parent.jog_lspeed
            if axis in {"A", "C"}:
                # TODO: check lin/ang mode
                speed = self.parent.jog_aspeed
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
            if self.ctype:
                if self.ctype.startswith("file:"):
                    self.parent.load_ngc(self.ctype[5:])
            elif self.text.lower() == "estop":
                self.parent.toggle_estop()
            elif self.text.lower() == "enable":
                self.parent.toggle_enable()
            elif self.text.lower() == "exit":
                if not self.enabled:
                    c.state(linuxcnc.STATE_ESTOP)
                exit(0)
            elif len(self.text) == 2 and self.text[0] in AXIS_NAMES and self.text[1] in {"+", "-"}:
                axis = AXIS_NAMES.index(self.text[0])
                c.jog(linuxcnc.JOG_STOP, jog_mode, axis)
        super().mouseReleaseEvent(event)


class GradientDRO(QLabel):
    def __init__(self, text=None, color1=None, color2=None, parent=None):
        super().__init__("", objectName="dro")
        self.parent = parent
        self.text = text
        self.values = {}

    def _groove_rect(self):
        return QRectF(0, 0, self.width(), self.height())

    def paintEvent(self, event):
        super().paintEvent(event)

        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        if not self.isEnabled():
            p.setOpacity(0.4)

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
            p.drawText(QRectF(40, py, self.width() - 80, pd), Qt.AlignRight, f"{values['pos']:0.3f} {self.parent.units}")
            py += pd

        font = QFont("Arial", 12)
        p.setFont(font)
        py = 60
        for name, values in self.values.items():
            p.drawText(QRectF(70, py, self.width() - 120, pd), Qt.AlignLeft, f"{'*' if values['homed'] else ''}")
            p.drawText(QRectF(80, py + 14, self.width() - 120, pd + 14), Qt.AlignLeft, f"{values['velocity']:0.1f} {self.parent.units}/s")
            py += pd


class GradientSlider(QSlider):
    def __init__(self, title=None, color1=None, color2=None, image=None, parent=None, objectName=None):
        super().__init__(Qt.Orientation.Horizontal, parent, objectName=objectName)
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
            return QSize(120, 60)
        return QSize(120, 40)

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
        font = QFont("Arial", 18, weight=QFont.Bold)
        p.setFont(font)
        p.setPen(QPen(Qt.white, 1))
        text = f"{self._fraction() * 100:2.0f}%"
        if self.pixmap:
            p.drawText(QRectF(10, self.height() - 40, self.width() - 20, 40), Qt.AlignLeft, text)
        else:
            p.drawText(QRectF(10, 10, self.width() - 20, self.height() - 20), Qt.AlignRight, text)

        if self.title:
            p.setFont(QFont("Arial", 12))
            if self.pixmap:
                p.drawText(QRectF(self.width() / 3, 10.0, self.width() / 3 * 2, 30.0), Qt.AlignCenter, self.title)
            else:
                p.drawText(QRectF(10, 10.0, self.width() - 20, self.height() - 20), Qt.AlignLeft, self.title)

        # text = "400mm/s"
        # p.drawText(QRectF(10, self.height() - 40, self.width() - 20, 40), Qt.AlignRight, text)
        if self.pixmap:
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
        elif self.title and self.title.split("-")[0].lower() == "linear":
            self.parent.jog_lspeed = self.value()
        elif self.title and self.title.split("-")[0].lower() == "angular":
            self.parent.jog_aspeed = self.value()

        self.is_moving = False


class JogImageXY(QLabel):
    def __init__(self, objectName=None):
        super().__init__("", objectName=objectName)

    def moveBegin(self, event):
        self.new_x = event.pos().x()
        self.new_y = event.pos().y()
        self.old_x = self.new_x
        self.old_y = self.new_y
        self.old_counts_x = h_next["axis.x.jog-counts"]
        self.old_counts_y = h_next["axis.y.jog-counts"]

    def moveEnd(self, event):
        pass

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.moveBegin(event)

    def mouseReleaseEvent(self, event):
        self.moveEnd(event)

    def mouseMoveEvent(self, event):
        diff_x = self.old_x - event.pos().x()
        diff_y = self.old_y - event.pos().y()
        s = 1.0
        z = 1.0
        offset_x = int(diff_x / z / s)
        offset_y = int(diff_y / z / s)
        x_scale = h_next["axis.x.jog-scale"]
        y_scale = h_next["axis.y.jog-scale"]
        if x_scale and y_scale:
            cal_x = h_next["axis.x.cal"]
            cal_y = h_next["axis.y.cal"]
            h_next["axis.x.jog-counts"] = self.old_counts_x + int(offset_x / x_scale * cal_x)
            h_next["axis.y.jog-counts"] = self.old_counts_y + int(offset_y / y_scale * cal_y)


class JogImageZ(QLabel):
    def __init__(self, objectName=None):
        super().__init__("", objectName=objectName)

    def moveBegin(self, event):
        self.new_z = event.pos().y()
        self.old_z = self.new_z
        self.old_counts_z = h_next["axis.z.jog-counts"]

    def moveEnd(self, event):
        pass

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.moveBegin(event)

    def mouseReleaseEvent(self, event):
        self.moveEnd(event)

    def mouseMoveEvent(self, event):
        diff_z = self.old_z - event.pos().y()
        s = 1.0
        z = 1.0
        offset_z = int(diff_z / z / s)
        z_scale = h_next["axis.z.jog-scale"]
        if z_scale:
            cal_z = h_next["axis.z.cal"]
            h_next["axis.z.jog-counts"] = self.old_counts_z + int(offset_z / z_scale * cal_z)


class ScreenHome(QWidget):
    def reload(self):
        cleanLayout(self.homev)
        home_top = QHBoxLayout()
        self.homev.addLayout(home_top, stretch=1)

        btn_back = GradientLabel("<-", parent=self.parent, objectName="back")
        btn_back.clicked.connect(partial(self.parent.view_set, "jog"))
        home_top.addWidget(btn_back, stretch=1)

        title = GradientLabel("Home", parent=self.parent, objectName="screentitle")
        home_top.addWidget(title, stretch=5)

        btn_space = GradientLabel("", parent=self.parent, objectName="btnnone")
        home_top.addWidget(btn_space, stretch=1)

        for n, pos in enumerate(s.position[: s.joints]):
            btn_home = GradientLabel(AXIS_NAMES[n], parent=self.parent, objectName="home")
            btn_home.clicked.connect(partial(do_homing, n))
            self.homev.addWidget(btn_home, stretch=1)

        home_all = GradientLabel("Home-ALL", parent=self.parent, objectName="homeall")
        home_all.clicked.connect(partial(do_homing, -1))
        self.homev.addWidget(home_all, stretch=1)

    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.homev = QVBoxLayout()
        self.setLayout(self.homev)


class CameraThread(QThread):
    image = pyqtSignal(np.ndarray)

    def __init__(self, device, options=None):
        super().__init__()
        self.device = device
        if not options:
            options = {}
        self.options = options
        self.width_source = options.get("width_source", 800)
        self.height_source = options.get("height_source", 600)
        self.capture = None

    def start_capture(self):
        self.capture = cv2.VideoCapture(self.device)
        self.capture.set(3, self.width_source)
        self.capture.set(4, self.height_source)

    def stop_capture(self):
        if self.capture:
            self.capture.release()
            self.capture = None

    def run(self):
        self.start_capture()
        while self.capture:
            try:
                ret, frame = self.capture.read()
                if ret:
                    self.image.emit(frame)
            except Exception as err:
                print("ERROR: camjog", err)

    def stop(self):
        self.stop_capture()


class ScreenTJog(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        jogv = QVBoxLayout()
        self.setLayout(jogv)

        jog_top = QHBoxLayout()
        jogv.addLayout(jog_top, stretch=1)

        btn_back = GradientLabel("<-", parent=self.parent, objectName="back")
        btn_back.clicked.connect(partial(self.parent.view_set, "jog"))
        jog_top.addWidget(btn_back, stretch=1)

        tjl = GradientLabel("Touch-JOG", parent=self.parent, objectName="screentitle")
        jog_top.addWidget(tjl, stretch=9)

        btn_space = GradientLabel("", parent=self.parent, objectName="btnnone")
        jog_top.addWidget(btn_space, stretch=1)

        jog_dro = QHBoxLayout()
        jogv.addLayout(jog_dro, stretch=1)

        self.pos_x = GradientLabel("X: ---", parent=self.parent, objectName="dro")
        jog_dro.addWidget(self.pos_x, stretch=1)
        self.pos_y = GradientLabel("Y: ---", parent=self.parent, objectName="dro")
        jog_dro.addWidget(self.pos_y, stretch=1)
        self.pos_z = GradientLabel("Z: ---", parent=self.parent, objectName="dro")
        jog_dro.addWidget(self.pos_z, stretch=1)

        jogh0 = QHBoxLayout()
        jogv.addLayout(jogh0, stretch=9)

        self.active = False
        self.img_xy = JogImageXY(objectName="jogxy")
        jogh0.addWidget(self.img_xy, stretch=9)

        img_z = JogImageZ(objectName="jogz")
        jogh0.addWidget(img_z, stretch=1)

        self.camera = CameraThread(0)
        self.camera.image.connect(self.update_image)
        self.camera.start()

    def update_image(self, frame):
        try:
            if not self.active:
                return

            # frame = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)

            s = 1.0
            z = 1.0
            w = self.img_xy.width() // 4 * 4
            h = self.img_xy.height()
            cx = w // 2
            cy = h // 2

            # scale image
            nw = int(w * s * z)
            nh = int(h * s * z)
            frame = cv2.resize(frame, (nw, nh), interpolation=cv2.INTER_LINEAR)

            # draw center lines
            cv2.line(frame, (0, nh // 2), (nw, nh // 2), (255, 0, 0), 1)
            cv2.line(frame, (nw // 2, 0), (nw // 2, nh), (255, 0, 0), 1)

            # center image
            offset_x = int(((cx * z) - cx) * s)
            offset_y = int(((cy * z) - cy) * s)
            frame = frame[offset_y : offset_y + int(h * s), offset_x : offset_x + int(w * s)]
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            image = QImage(frame, frame.shape[1], frame.shape[0], QImage.Format_RGB888)
            self.img_xy.setPixmap(QPixmap.fromImage(image))
        except Exception as err:
            print("ERROR: UPDATE IMAGE: ", err)


class ScreenJog(QWidget):
    def __init__(self, parent):
        super().__init__(objectName="jogbg")
        self.parent = parent
        jogv = QVBoxLayout()
        self.setLayout(jogv)

        jogh0 = QHBoxLayout()
        jogv.addLayout(jogh0, stretch=1)

        xp = GradientLabel("A+", objectName="btnjog", parent=self.parent)
        jogh0.addWidget(xp, stretch=1)
        xp = GradientLabel("C+", objectName="btnjog", parent=self.parent)
        jogh0.addWidget(xp, stretch=1)

        jogh1 = QHBoxLayout()
        jogv.addLayout(jogh1, stretch=1)
        xp = GradientLabel("A-", objectName="btnjog", parent=self.parent)
        jogh1.addWidget(xp, stretch=1)
        xp = GradientLabel("C-", objectName="btnjog", parent=self.parent)
        jogh1.addWidget(xp, stretch=1)

        jogh2 = QHBoxLayout()
        jogv.addLayout(jogh2, stretch=2)
        btn_tjog = GradientLabel("TJOG", objectName="btntjog", parent=self.parent)
        btn_tjog.clicked.connect(partial(self.parent.view_set, "tjog"))
        jogh2.addWidget(btn_tjog, stretch=1)
        xp = GradientLabel("Y+", objectName="btnjog", parent=self.parent)
        jogh2.addWidget(xp, stretch=1)
        xp = GradientLabel("Z+", objectName="btnjog", parent=self.parent)
        jogh2.addWidget(xp, stretch=1)

        jogh3 = QHBoxLayout()
        jogv.addLayout(jogh3, stretch=2)
        xp = GradientLabel("X-", objectName="btnjog", parent=self.parent)
        jogh3.addWidget(xp, stretch=1)
        xp = GradientLabel("", objectName="none")
        jogh3.addWidget(xp, stretch=1)
        xp = GradientLabel("X+", objectName="btnjog", parent=self.parent)
        jogh3.addWidget(xp, stretch=1)

        jogh4 = QHBoxLayout()
        jogv.addLayout(jogh4, stretch=2)
        btn_home = GradientLabel("HOME", objectName="btnhome")
        btn_home.clicked.connect(partial(self.parent.view_set, "home"))
        jogh4.addWidget(btn_home, stretch=1)
        ym = GradientLabel("Y-", objectName="btnjog", parent=self.parent)
        jogh4.addWidget(ym, stretch=1)
        zm = GradientLabel("Z-", objectName="btnjog", parent=self.parent)
        jogh4.addWidget(zm, stretch=1)

        lslider_jog = GradientSlider(title="Linear-Speed", parent=self.parent, objectName="linear")
        lslider_jog.setRange(0, int(parent.linear_velocity_max))
        lslider_jog.setValue(int(parent.linear_velocity_default))
        jogv.addWidget(lslider_jog, stretch=1)

        aslider_jog = GradientSlider(title="Angular-Speed", parent=self.parent, objectName="angular")
        aslider_jog.setRange(0, int(parent.angular_velocity_max))
        aslider_jog.setValue(int(parent.angular_velocity_default))
        jogv.addWidget(aslider_jog, stretch=1)


class ScreenMdi(QWidget):
    mdi_commands = []

    def history_reload(self):
        history_file = os.path.join(os.path.expanduser("~"), ".axis_mdi_history")
        if os.path.isfile(history_file):
            self.mdi_commands = []
            for cmd in open(history_file, "r").read().split("\n"):
                if cmd:
                    self.mdi_commands.append(cmd)
        self.mdi_commands = self.mdi_commands[:100]
        self.history.clear()
        last_item = None
        for cmd in self.mdi_commands:
            last_item = QListWidgetItem(cmd)
            self.history.addItem(last_item)
        if last_item is not None:
            self.history.scrollToItem(last_item)

    def history_add(self, command):
        if self.mdi_commands and self.mdi_commands[-1] != command:
            self.mdi_commands = self.mdi_commands[:100]
            self.mdi_commands.append(command)
            history_file = os.path.join(os.path.expanduser("~"), ".axis_mdi_history")
            open(history_file, "w").write("\n".join(self.mdi_commands))
            self.history_reload()

    def hselect(self, item):
        self.cmdline.setText(item.text())

    def hrun(self, item):
        self.cmdline.setText(item.text())
        self.run_cmd()

    def stop_cmd(self):
        c.abort()

    def run_cmd(self):
        command = self.cmdline.text()
        if ok_for_mdi():
            c.mode(linuxcnc.MODE_MDI)
            c.wait_complete()
            c.mdi(command)
            self.history_add(command)
            self.cmdline.setText("")
        else:
            print("ERROR: run_cmd:", command)

    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        self.setLayout(layout)

        self.history = QListWidget()
        layout.addWidget(self.history)
        self.history_reload()

        self.history.itemClicked.connect(self.hselect)
        self.history.itemDoubleClicked.connect(self.hrun)

        cmd_layout = QHBoxLayout()
        layout.addLayout(cmd_layout)

        self.cmdline = QLineEdit()
        self.cmdline.returnPressed.connect(self.run_cmd)
        cmd_layout.addWidget(self.cmdline)

        btn_cmd = QPushButton("RUN", objectName="run")
        btn_cmd.clicked.connect(self.run_cmd)
        cmd_layout.addWidget(btn_cmd)

        btn_stop = QPushButton("STOP", objectName="stop")
        btn_stop.clicked.connect(self.stop_cmd)
        cmd_layout.addWidget(btn_stop)


class ScreenFiles(QWidget):
    selected = None

    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        layout = QVBoxLayout()
        self.setLayout(layout)

        buttons = QHBoxLayout()
        layout.addLayout(buttons)

        btn_load = GradientLabel("LOAD", parent=self.parent, objectName="fileload")
        btn_load.clicked.connect(self.load)
        buttons.addWidget(btn_load)

        btn_cancel = GradientLabel("CANCEL", parent=self.parent, objectName="filecancel")
        btn_cancel.clicked.connect(self.cancel)
        buttons.addWidget(btn_cancel)

        filelist = QWidget(objectName="filebg")
        self.filelist_layout = QVBoxLayout()
        filelist.setLayout(self.filelist_layout)
        scroll = QScrollArea()
        scroll.setWidget(filelist)
        scroll.setWidgetResizable(True)
        layout.addWidget(scroll)

        # self.reload()

    def reload(self):
        cleanLayout(self.filelist_layout)
        files = glob.glob(os.path.join(os.path.expanduser("~"), "*.ngc"))
        files.sort(key=os.path.getmtime)
        for filename in reversed(files):
            entry_layout = QHBoxLayout()
            self.filelist_layout.addLayout(entry_layout, stretch=1)

            if os.path.isfile(f"{filename}.svg"):
                preview = QtSvg.QSvgWidget(f"{filename}.svg")
            else:
                preview = GradientLabel("", parent=self.parent, objectName="filenoimg")
            preview.setFixedHeight(175)
            entry_layout.addWidget(preview, stretch=1)

            entry_label = GradientFileEntry(filename)
            entry_label.clicked.connect(partial(self.preview, filename, entry_label))
            entry_layout.addWidget(entry_label, stretch=4)

    def preview(self, filename, widget=None):
        self.selected = filename
        self.parent.glview.load(filename, widget)

    def load(self):
        self.parent.load_ngc(self.selected)

    def cancel(self):
        self.parent.glview.load(self.parent.ngc_file)
        self.parent.view_set("jog")


class SliderProxyStyle(QProxyStyle):
    def pixelMetric(self, metric, option, widget):
        if metric in {QStyle.PM_SliderThickness, QStyle.PM_SliderLength}:
            return 40
        return super().pixelMetric(metric, option, widget)


class ScreenVcpTab(QWidget):
    def __init__(self, tab, halpins_in):
        super().__init__(objectName="vcp")

        layout = QVBoxLayout()
        self.setLayout(layout)

        def next_element(element, layout, prefix=""):
            for child in element:
                # print(prefix, child.tag, child.attrib)
                if child.tag == "label":
                    text = ""
                    anchor = "c"
                    # width = ""
                    for child2 in child:
                        if child2.tag == "format":
                            vformat = child2.text.strip('"')
                        elif child2.tag == "anchor":
                            anchor = child2.text.strip('"')
                        elif child2.tag == "text":
                            text = child2.text.strip('"')
                        # elif child2.tag == "width":
                        #    width = child2.text.strip('"')
                    label = QLabel(text, objectName="vcp_label")
                    # if width:
                    # label.setFixedWidth(int(width) * 12)
                    if anchor == "e":
                        label.setAlignment(Qt.AlignRight)
                    elif anchor == "w":
                        label.setAlignment(Qt.AlignLeft)
                    elif anchor == "c":
                        label.setAlignment(Qt.AlignCenter)
                    label.setFixedHeight(45)
                    layout.addWidget(label)
                elif child.tag in {"led", "rectled"}:
                    on_color = QColor(0, 255, 0)
                    off_color = QColor(0, 0, 0)
                    for child2 in child:
                        if child2.tag == "on_color":
                            on_color = QColor(child2.text.strip('"'))
                        if child2.tag == "off_color":
                            off_color = QColor(child2.text.strip('"'))
                    label = LED(on_color=on_color, off_color=off_color, ltype=child.tag, objectName="vcp_led")
                    layout.addWidget(label)
                    for child2 in child:
                        if child2.tag == "halpin":
                            halpin = child2.text.strip('"')
                            h_vcp.newpin(f"{halpin}", hal.HAL_BIT, hal.HAL_IN)
                            halpins_in[halpin] = (child.tag, label)
                elif child.tag in {"number", "s32", "u32"}:
                    anchor = "c"
                    vformat = "0.0f"
                    for child2 in child:
                        if child2.tag == "format":
                            vformat = child2.text.strip('"')
                        elif child2.tag == "anchor":
                            anchor = child2.text.strip('"')
                    label = QLabel("<NUMBER>", objectName="vcp_number")
                    if anchor == "e":
                        label.setAlignment(Qt.AlignRight)
                    elif anchor == "w":
                        label.setAlignment(Qt.AlignLeft)
                    elif anchor == "c":
                        label.setAlignment(Qt.AlignCenter)
                    layout.addWidget(label)
                    for child2 in child:
                        if child2.tag == "halpin":
                            halpin = child2.text.strip('"')
                            if child.tag in {"s32"}:
                                h_vcp.newpin(f"{halpin}", hal.HAL_S32, hal.HAL_IN)
                            elif child.tag in {"u32"}:
                                h_vcp.newpin(f"{halpin}", hal.HAL_U32, hal.HAL_IN)
                            else:
                                h_vcp.newpin(f"{halpin}", hal.HAL_FLOAT, hal.HAL_IN)
                            halpins_in[halpin] = (child.tag, label, vformat)
                elif child.tag == "multilabel":
                    label = QLabel("<MULTILABEL>", objectName="vcp_multilabel")
                    label.setAlignment(Qt.AlignCenter)
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
                                h_vcp.newpin(f"{halpin}.legend{legend_n}", hal.HAL_BIT, hal.HAL_IN)
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
                    label = QProgressBar(objectName="vcp_bar")
                    label.setMinimum(int(vmin) * 10)
                    label.setMaximum(int(vmax) * 10)
                    label.setValue(50 * 10)
                    layout.addWidget(label)
                    for child2 in child:
                        if child2.tag == "halpin":
                            halpin = child2.text.strip('"')
                            h_vcp.newpin(f"{halpin}", hal.HAL_FLOAT, hal.HAL_IN)
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
                    label = QSlider(Qt.Orientation.Horizontal, objectName="vcp_scale")
                    label.setStyle(SliderProxyStyle(label.style()))
                    label.setMinimum(int(vmin) * 10)
                    label.setMaximum(int(vmax) * 10)
                    label.setValue(int(initval) * 10)
                    layout.addWidget(label)
                    for child2 in child:
                        if child2.tag == "halpin":
                            halpin = child2.text.strip('"')
                            h_vcp.newpin(f"{halpin}-i", hal.HAL_S32, hal.HAL_OUT)
                            h_vcp.newpin(f"{halpin}-f", hal.HAL_FLOAT, hal.HAL_OUT)

                            def change(halpin, val):
                                h_vcp[f"{halpin}-i"] = int(val / 10)
                                h_vcp[f"{halpin}-f"] = val / 10

                            label.valueChanged.connect(partial(change, halpin))

                elif child.tag == "checkbutton":
                    checkbox = QPushButton(objectName="vcp_checkbutton")
                    checkbox.setCheckable(True)
                    layout.addWidget(checkbox)
                    for child2 in child:
                        if child2.tag == "halpin":
                            halpin = child2.text.strip('"')
                            h_vcp.newpin(f"{halpin}", hal.HAL_BIT, hal.HAL_OUT)

                            def change(halpin, val):
                                h_vcp[f"{halpin}"] = val
                                # if val:
                                #    checkbox.setStyleSheet("background-color : red")
                                # else:
                                #    checkbox.setStyleSheet("background-color : lightblue")

                            checkbox.clicked.connect(partial(change, halpin))
                    # checkbox.setStyleSheet("background-color : lightblue")

                elif child.tag == "button":
                    text = ""
                    for child2 in child:
                        if child2.tag == "text":
                            text = child2.text.strip('"')
                    button = QPushButton(text, objectName="vcp_button")
                    layout.addWidget(button)

                    for child2 in child:
                        if child2.tag == "halpin":
                            halpin = child2.text.strip('"')
                            h_vcp.newpin(f"{halpin}", hal.HAL_BIT, hal.HAL_OUT)

                            def change(halpin, val):
                                h_vcp[f"{halpin}"] = val

                            button.pressed.connect(partial(change, halpin, True))
                            button.released.connect(partial(change, halpin, False))

                elif child.tag == "labelframe":
                    frame = QGroupBox(objectName="vcp_labelframe")
                    frame.setTitle(child.attrib["text"])
                    vbox = QVBoxLayout()
                    vbox.setContentsMargins(5, 15, 5, 0)
                    frame.setLayout(vbox)
                    layout.addWidget(frame)
                    next_element(child, vbox, prefix=" " + prefix)
                elif child.tag == "hbox":
                    hbox = QHBoxLayout()
                    layout.addLayout(hbox)
                    next_element(child, hbox, prefix=" " + prefix)
                elif child.tag == "vbox":
                    vbox = QVBoxLayout()
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
        self.setLayout(layout)

        self.slider_feed = GradientSlider(title="Feed-Overwrite", image="touchprobe.png")
        self.slider_feed.setRange(0, 300)
        layout.addWidget(self.slider_feed, stretch=2)

        self.slider_rapid = GradientSlider(title="Rapid-Overwrite", image="jogwheel.png")
        self.slider_rapid.setRange(0, 100)
        layout.addWidget(self.slider_rapid, stretch=2)

        self.slider_spindle = GradientSlider(title="Spindle-Overwrite", image="valve.png")
        self.slider_spindle.setRange(0, 300)
        layout.addWidget(self.slider_spindle, stretch=2)


class ScreenDro(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        layout = QVBoxLayout()
        self.setLayout(layout)
        self.dro = GradientDRO("Position", parent=parent)
        layout.addWidget(self.dro, stretch=3)


class ScreenNgc(QWidget):
    def __init__(self, parent):
        super().__init__()
        layout = QVBoxLayout()
        self.setLayout(layout)

        hbox = QHBoxLayout()
        layout.addLayout(hbox, stretch=5)

        btn_open = QPushButton(QIcon("open.png"), "OPEN", objectName="progopen")
        # btn_open.setStyleSheet("background-color: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1, stop: 0 #78a023, stop: 1 #9fc31b); height: 50px;")
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

        btn_run = QPushButton(QIcon("play.png"), "RUN", objectName="progrun")
        # btn_run.setStyleSheet("background-color: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1, stop: 0 #78a023, stop: 1 #9fc31b); height: 50px;")
        btn_run.clicked.connect(partial(prog_mode, "RUN"))
        hbox.addWidget(btn_run, stretch=0)

        btn_pause = QPushButton(QIcon("pause.png"), "PAUSE", objectName="progpause")
        # btn_pause.setStyleSheet("background-color: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1, stop: 0 #78a023, stop: 1 #9fc31b); height: 50px;")
        btn_pause.clicked.connect(partial(prog_mode, "PAUSE"))
        hbox.addWidget(btn_pause, stretch=0)

        btn_step = QPushButton(QIcon("step.png"), "STEP", objectName="progstep")
        # btn_step.setStyleSheet("background-color: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1, stop: 0 #78a023, stop: 1 #9fc31b); height: 50px;")
        btn_step.clicked.connect(partial(prog_mode, "STEP"))
        hbox.addWidget(btn_step, stretch=0)

        btn_stop = QPushButton(QIcon("stop.png"), "STOP", objectName="progstop")
        # btn_stop.setStyleSheet("background-color: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1, stop: 0 #78a023, stop: 1 #9fc31b); height: 50px;")
        btn_stop.clicked.connect(partial(prog_mode, "STOP"))
        hbox.addWidget(btn_stop, stretch=0)

        self.editor = QPlainTextEdit()
        # self.editor.setStyleSheet("""
        #    QPlainTextEdit {
        #        background-color: #2b2b2b;
        #        color: #ffffff;
        #        font-family: 'Consolas', 'Courier New', monospace;
        #        font-size: 12pt;
        #    }
        # """)
        layout.addWidget(self.editor, stretch=5)


class PyVCP:
    def __init__(self, layout, xml_file, parent):
        self.parent = parent
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
                        scroll.setWidget(self.screen_status)
                        scroll.setWidgetResizable(True)
                        self.layout.addWidget(scroll)
                        tab_n += 1

    def update(self):
        for pin, data in self.halpins_in.items():
            if data[0] in {"led", "rectled"}:
                val = h_vcp[f"{pin}"]
                if val:
                    data[1].on = True
                else:
                    data[1].on = False
                data[1].update()
            elif data[0] == "bar":
                val = h_vcp[f"{pin}"]
                data[1].setValue(int(val * 10))

            elif data[0] in {"number", "s32", "u32"}:
                val = h_vcp[f"{pin}"]
                vformat = data[2]
                if vformat == "d":
                    vformat = "0.0f"
                data[1].setText(f"{{value:{vformat}}}".format(value=val))
            elif data[0] == "multilabel":
                for legend_n, legend_name in enumerate(data[2]):
                    val = h_vcp[f"{pin}.legend{legend_n}"]
                    if val is True:
                        data[1].setText(legend_name)
            else:
                print("missing:", pin, data, val)

    def buttons(self, layout):
        def setTab(idx):
            self.parent.center_stack.setCurrentIndex(0)
            self.layout.setCurrentIndex(idx)

        for tab_n, tabname in enumerate(self.tabnames):
            btn_status = GradientLabel(tabname, parent=self.parent)
            btn_status.clicked.connect(partial(setTab, tab_n))
            layout.addWidget(btn_status, stretch=1)


class MainWindow(QMainWindow):
    last_offsets = []
    ngc_file = ""
    jog_lspeed = 40
    jog_aspeed = 5

    def __init__(self, args):
        super().__init__()
        self.setWindowTitle("RIO-Next")
        self.resize(1200, 1920)
        #self.resize(800, 1080)

        s.poll()
        self.ini_filename = s.ini_filename
        if args.ini:
            self.ini_filename = args.ini

        self.inifile = linuxcnc.ini(self.ini_filename)
        xml_file = self.inifile.find("DISPLAY", "PYVCP")
        self.units = self.inifile.find("TRAJ", "LINEAR_UNITS")
        self.linear_velocity_default = float(self.inifile.find("TRAJ", "DEFAULT_LINEAR_VELOCITY") or 10.0)
        self.linear_velocity_max = float(self.inifile.find("TRAJ", "MAX_LINEAR_VELOCITY") or 20.0)
        self.angular_velocity_default = float(self.inifile.find("TRAJ", "DEFAULT_ANGULAR_VELOCITY") or 5.0)
        self.angular_velocity_max = float(self.inifile.find("TRAJ", "MAX_ANGULAR_VELOCITY") or 10.0)

        mw = QWidget(objectName="main")
        mw.setStyleSheet(stylesheet)
        main_layout = QVBoxLayout(mw)
        self.setCentralWidget(mw)

        title_layout = QHBoxLayout()
        main_layout.addLayout(title_layout, stretch=0)

        top_layout = QHBoxLayout()
        main_layout.addLayout(top_layout, stretch=1)

        self.center_stack = QStackedWidget()
        main_layout.addWidget(self.center_stack, stretch=3)

        self.center_widget = QWidget()
        self.center_layout = QVBoxLayout()
        self.center_widget.setLayout(self.center_layout)
        self.center_stack.addWidget(self.center_widget)

        center1_layout = QHBoxLayout()
        self.center_layout.addLayout(center1_layout, stretch=1)
        center1l_layout = QVBoxLayout()
        center1_layout.addLayout(center1l_layout, stretch=1)
        center1r_layout = QVBoxLayout()
        center1_layout.addLayout(center1r_layout, stretch=1)

        center2_layout = QHBoxLayout()
        self.center_layout.addLayout(center2_layout, stretch=2)
        center2l_layout = QVBoxLayout()
        center2_layout.addLayout(center2l_layout, stretch=1)
        center2r_layout = QVBoxLayout()
        center2_layout.addLayout(center2r_layout, stretch=1)

        bottom_layout = QHBoxLayout()
        main_layout.addLayout(bottom_layout, stretch=0)

        bottoml_layout = QHBoxLayout()
        bottom_layout.addLayout(bottoml_layout, stretch=1)

        bottomr_layout = QHBoxLayout()
        bottom_layout.addLayout(bottomr_layout, stretch=1)

        self.estop = GradientLabel("ESTOP", objectName="estop", parent=self)
        title_layout.addWidget(self.estop, stretch=1)
        toggle_estop_action = QAction("Toggle Estop", self)
        toggle_estop_action.setShortcut("F1")
        toggle_estop_action.triggered.connect(self.toggle_estop)
        self.addAction(toggle_estop_action)

        self.enable = GradientLabel("ENABLE", objectName="enable", parent=self)
        title_layout.addWidget(self.enable, stretch=1)
        toggle_enable_action = QAction("Toggle Enable", self)
        toggle_enable_action.setShortcut("F2")
        toggle_enable_action.triggered.connect(self.toggle_enable)
        self.addAction(toggle_enable_action)

        title = GradientLabel("LinuxCNC - RIO", objectName="screentitle")
        title_layout.addWidget(title, stretch=9)
        self.exit = GradientLabel("EXIT", objectName="exit", parent=self)
        title_layout.addWidget(self.exit, stretch=1)

        self.glview = View3D()
        top_layout.addWidget(self.glview, stretch=1)

        self.center1l_stack = QStackedWidget()
        center1l_layout.addWidget(self.center1l_stack, stretch=1)
        self.screen_overwrites = ScreenOverwrites()
        self.center1l_stack.addWidget(self.screen_overwrites)

        self.center1r_stack = QStackedWidget()
        center1r_layout.addWidget(self.center1r_stack, stretch=1)
        self.screen_dro = ScreenDro(self)
        self.center1r_stack.addWidget(self.screen_dro)

        self.center2l_stack = QStackedWidget()
        center2l_layout.addWidget(self.center2l_stack, stretch=1)
        self.screen_jog = ScreenJog(self)
        self.center2l_stack.addWidget(self.screen_jog)
        self.screen_mdi = ScreenMdi()
        self.center2l_stack.addWidget(self.screen_mdi)
        self.screen_ngc = ScreenNgc(self)
        self.center2l_stack.addWidget(self.screen_ngc)

        self.screen_home = ScreenHome(self)
        self.center2l_stack.addWidget(self.screen_home)

        self.screen_files = ScreenFiles(self)
        self.center_stack.addWidget(self.screen_files)

        self.screen_tjog = ScreenTJog(self)
        self.center_stack.addWidget(self.screen_tjog)

        self.center2r_stack = QStackedWidget()
        center2r_layout.addWidget(self.center2r_stack, stretch=1)

        self.pyvcp = None
        if xml_file:
            self.pyvcp = PyVCP(self.center2r_stack, xml_file, self)

        btn_jog = GradientLabel("JOG", objectName="btnjog")
        btn_jog.clicked.connect(partial(self.view_set, "jog"))
        bottoml_layout.addWidget(btn_jog, stretch=1)

        btn_mdi = GradientLabel("MDI", objectName="btnmdi")
        btn_mdi.clicked.connect(partial(self.view_set, "mdi"))
        bottoml_layout.addWidget(btn_mdi, stretch=1)

        def open_prog():
            if not os.path.isfile(self.ngc_file):
                self.view_set("files")
            else:
                self.view_set("prog")

        btn_prog = GradientLabel("PROG", objectName="btnprog")
        btn_prog.clicked.connect(open_prog)
        bottoml_layout.addWidget(btn_prog, stretch=1)

        btn_files = GradientLabel("FILES", objectName="btnfiles")
        btn_files.clicked.connect(partial(self.view_set, "files"))
        bottoml_layout.addWidget(btn_files, stretch=1)

        glabel2 = GradientLabel("", objectName="btnnone")
        bottoml_layout.addWidget(glabel2, stretch=1)

        if self.pyvcp:
            self.pyvcp.buttons(bottomr_layout)

        self.postgui()

        self.timer = QTimer()
        self.timer.timeout.connect(self.runTimer)
        self.timer.start(100)

    def view_set(self, mode):
        views = {
            "jog": (0, 0, None),
            "mdi": (0, 1, None),
            "prog": (0, 2, None),
            "home": (0, 3, None),
            "files": (1, None, None),
            "tjog": (2, None, None),
        }
        if view := views.get(mode):
            if view[0] is not None:
                self.center_stack.setCurrentIndex(view[0])
            if view[1] is not None:
                self.center2l_stack.setCurrentIndex(view[1])
            if view[2] is not None:
                self.center2r_stack.setCurrentIndex(view[2])
        if mode == "files":
            self.screen_files.reload()
        if mode == "home":
            self.screen_home.reload()
        self.screen_tjog.active = bool(mode == "tjog")

    def postgui(self):
        for filename in self.inifile.findall("HAL", "POSTGUI_HALFILE") or []:
            ini_dir = os.path.dirname(self.ini_filename)
            haltcl = ["haltcl", "-i", ini_dir, "-f", str(filename)]
            if filename.split(".")[-1] == "tcl":
                haltcl = ["haltcl", "-i", ini_dir, str(filename)]
            ret = os.spawnvp(os.P_WAIT, "halcmd", haltcl)
            if ret != 0:
                raise SystemExit(ret)

    def load_ngc(self, filename=None):
        if not filename:
            file_dialog = QFileDialog(self)
            name = file_dialog.getOpenFileName(
                self,
                "Load a gCode file",
                "./",
                "gCode (*.ngc)",
            )
            filename = name[0]
        if filename:
            self.ngc_file = filename
            if os.path.isfile(self.ngc_file):
                self.glview.load(self.ngc_file)
                self.screen_ngc.editor.setPlainText(open(self.ngc_file, "r").read())
                c.program_open(self.ngc_file)
                self.center_stack.setCurrentIndex(0)
                self.center2l_stack.setCurrentIndex(2)

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
            if "X" in values:
                self.screen_tjog.pos_x.setText(f"X: {values['X']['pos']:0.3f} {self.units}")
            if "Y" in values:
                self.screen_tjog.pos_y.setText(f"Y: {values['Y']['pos']:0.3f} {self.units}")
                self.screen_tjog.pos_y.update()
            if "Z" in values:
                self.screen_tjog.pos_z.setText(f"Z: {values['Z']['pos']:0.3f} {self.units}")

        if self.estop.enabled != s.estop:
            self.estop.enabled = s.estop
            if self.estop.enabled:
                self.estop.setStyleSheet("background-color : red")
            else:
                self.estop.setStyleSheet("")

            self.estop.update()

        if self.enable.enabled != s.enabled:
            self.enable.enabled = s.enabled
            if self.enable.enabled:
                self.enable.setStyleSheet("")
            else:
                self.enable.setStyleSheet("background-color: red")

            self.enable.update()

        if self.pyvcp:
            self.pyvcp.update()

    def toggle_estop(self):
        s.poll()
        if s.estop:
            c.state(linuxcnc.STATE_ESTOP_RESET)
        else:
            c.state(linuxcnc.STATE_ESTOP)

    def toggle_enable(self):
        s.poll()
        if s.enabled:
            c.state(linuxcnc.STATE_OFF)
        else:
            c.state(linuxcnc.STATE_ON)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-ini", help="ini file", type=str, default=None)
    parser.add_argument("--fullscreen", help="fullscreen", action="store_true")
    args = parser.parse_args()

    app = QApplication(sys.argv)
    window = MainWindow(args)
    h_vcp.ready()
    h_next.ready()
    if args.fullscreen:
        # window.showFullScreen()
        window.show()
    else:
        window.show()
    sys.exit(app.exec_())
