#!/usr/bin/env python3
#
#
"""EMBED_TAB_NAME=CamJog
EMBED_TAB_COMMAND=halcmd loadusr -Wn camjog /data2/src/ICE40-2023/serial-tx/riocore/camjog.py --xid {XID} --camera USB2.0 --width 640 --height 480 --scale 1.5

net camjog_x <= camjog.axis.x.jog-counts
net camjog_x => joint.0.jog-counts
net camjog_x => axis.x.jog-counts
setp camjog.axis.x.cal 0.1
setp joint.0.jog-vel-mode 0
setp joint.0.jog-enable 1
setp joint.0.jog-scale 0.01
setp axis.x.jog-vel-mode 0
setp axis.x.jog-enable 1
setp axis.x.jog-scale 0.15

net camjog_y <= camjog.axis.y.jog-counts
net camjog_y => joint.1.jog-counts
net camjog_y => axis.y.jog-counts
setp camjog.axis.y.cal 0.1
setp joint.1.jog-vel-mode 0
setp joint.1.jog-enable 1
setp joint.1.jog-scale 0.01
setp axis.y.jog-vel-mode 0
setp axis.y.jog-enable 1
setp axis.y.jog-scale -0.15

"""

import argparse
import math
import os
import json
import signal
import serial
import sys
from functools import partial

import cv2
import numpy as np
from PyQt5.QtCore import QThread, Qt, pyqtSignal, QTimer
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import (
    QMainWindow,
    QApplication,
    QComboBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

parser = argparse.ArgumentParser()
parser.add_argument("--xid", "-x", help="parent x window id", type=int)
parser.add_argument("--video", "-v", help="video device id", type=int, default=-1)
parser.add_argument("--camera", "-c", help="video device name", type=str, default="")
parser.add_argument("--width", "-W", help="video device width", type=int, default=640)
parser.add_argument("--height", "-H", help="video device height", type=int, default=480)
parser.add_argument("--scale", "-S", help="scale image", type=float, default=1.0)
parser.add_argument("--fullscreen", "-f", help="fullscreen mode", default=False, action="store_true")
parser.add_argument("--rotate", "-r", help="rotate screen", default=False, action="store_true")
parser.add_argument("--name", "-n", help="component name", type=str, default="camjog")
parser.add_argument("--server", "-s", help="remote server (rmpg)", type=str, default="")
parser.add_argument("--device", "-d", help="device", type=str, default="")
parser.add_argument("--baud", "-b", help="baudrate", type=int, default=115200)

args = parser.parse_args()

offset_x = -22.9
offset_y = 55.45


if args.server:
    import rhal as hal

    print("camjog: remote mode")

    h = hal.component(args.server)
    cal_x = 0.15
    cal_y = -0.13
else:
    try:
        import hal

        h = hal.component(args.name)
        h.newpin("axis.x.jog-counts", hal.HAL_S32, hal.HAL_OUT)
        h.newpin("axis.y.jog-counts", hal.HAL_S32, hal.HAL_OUT)
        h.newpin("axis.x.jog-scale", hal.HAL_FLOAT, hal.HAL_IN)
        h.newpin("axis.y.jog-scale", hal.HAL_FLOAT, hal.HAL_IN)
        h.newpin("axis.x.cal", hal.HAL_FLOAT, hal.HAL_IN)
        h.newpin("axis.y.cal", hal.HAL_FLOAT, hal.HAL_IN)
        for overwrite in ("feed-override", "rapid-override", "spindle.0.override", "max-velocity"):
            h.newpin(f"{overwrite}.counts", hal.HAL_S32, hal.HAL_OUT)
            h.newpin(f"{overwrite}.value", hal.HAL_FLOAT, hal.HAL_IN)
        h.newpin("sw0", hal.HAL_BIT, hal.HAL_OUT)
        h.newpin("sw0-not", hal.HAL_BIT, hal.HAL_OUT)
        h.ready()
        no_hal = False
    except Exception:
        # for testing
        no_hal = True
        h = {}
        h["axis.x.jog-counts"] = 1
        h["axis.y.jog-counts"] = 1
        h["axis.x.jog-scale"] = 1.0
        h["axis.y.jog-scale"] = 1.0
        h["axis.x.cal"] = 0.1
        h["axis.y.cal"] = 0.1
        for overwrite in ("feed-override", "rapid-override", "spindle.0.override", "max-velocity"):
            h[f"{overwrite}.counts"] = 0
            h[f"{overwrite}.value"] = 50.0
        h["sw0"] = 0
        h["sw0-not"] = 1


TWO_PI = math.pi * 2


def line_center_2d(p_1, p_2):
    """Gets the center point between 2 points in 2D."""
    center_x = (p_1[0] + p_2[0]) / 2
    center_y = (p_1[1] + p_2[1]) / 2
    return (center_x, center_y)


def angle_of_line(p_1, p_2):
    """Gets the angle of a single line."""
    return math.atan2(p_2[1] - p_1[1], p_2[0] - p_1[0])


def angle_2d(p_1, p_2):
    """Gets the angle of a single line (2nd version)."""
    theta1 = math.atan2(p_1[1], p_1[0])
    theta2 = math.atan2(p_2[1], p_2[0])
    dtheta = theta2 - theta1
    while dtheta > math.pi:
        dtheta -= TWO_PI
    while dtheta < -math.pi:
        dtheta += TWO_PI
    return dtheta


def is_inside_polygon(polygon, point):
    """Checks if a point is inside an polygon."""
    angle = 0.0
    point_0 = point[0]
    point_1 = point[1]
    last = polygon[0]
    for nextp in polygon[1:]:
        angle += angle_2d(
            (last[0] - point_0, last[1] - point_1),
            (nextp[0] - point_0, nextp[1] - point_1),
        )
        last = nextp
    return bool(abs(angle) >= math.pi)


class MyImage(QLabel):
    def __init__(self, parent):
        super(QLabel, self).__init__(parent)
        self.parent = parent
        self.list_x = [0] * 10
        self.list_y = [0] * 10

    def resizeEvent(self, event):
        pass
        # print(self.width(), self.height())

    def wheelEvent(self, event):
        delta = event.angleDelta()
        # mp_x = event.pos().x()
        # mp_y = event.pos().y()
        if delta.y() < 0:
            if self.parent.options["zoom"] > 1.0:
                self.parent.options["zoom"] -= 0.1
            self.parent.options["zoom"] = max(self.parent.options["zoom"], 1.0)
        elif self.parent.options["zoom"] < 10.0:
            self.parent.options["zoom"] += 0.1

        self.parent.zoom_label.setText(f"{self.parent.options['zoom']:0.1f}")

    def moveBegin(self, event):
        global cal_x
        global cal_y
        self.new_x = event.pos().x()
        self.new_y = event.pos().y()
        self.old_x = self.new_x
        self.old_y = self.new_y
        self.old_counts_x = h["axis.x.jog-counts"]
        self.old_counts_y = h["axis.y.jog-counts"]

        (offset_x, offset_y) = self.parent.convert_to_cam((self.new_x, self.new_y))

        if self.parent.options["mode"] == "goto":
            x_scale = h["axis.x.jog-scale"]
            y_scale = h["axis.y.jog-scale"]
            if x_scale and y_scale:
                if not args.server:
                    cal_x = h["axis.x.cal"]
                    cal_y = h["axis.y.cal"]
                h["axis.x.jog-counts"] += int(offset_x / x_scale * cal_x)
                h["axis.y.jog-counts"] += int(offset_y / y_scale * cal_y)

        elif self.parent.options["mode"] == "touch":
            self.parent.options["points"] = []
            self.parent.options["touch"] = (offset_x, offset_y)
            self.parent.options["mode"] = "edges"

        elif self.parent.options["mode"] == "edges":
            if len(self.parent.options["points"]) > 3:
                self.parent.options["points"] = []
            self.parent.options["points"].append((offset_x, offset_y))

    def moveEnd(self, event):
        pass

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.moveBegin(event)

    def mouseReleaseEvent(self, event):
        self.moveEnd(event)

    def mouseMoveEvent(self, event):
        global cal_x
        global cal_y
        if self.parent.options["mode"] == "move":
            diff_x = self.old_x - event.pos().x()
            diff_y = self.old_y - event.pos().y()
            s = self.parent.options["scale"]
            z = self.parent.options["zoom"]
            offset_x = int(diff_x / z / s)
            offset_y = int(diff_y / z / s)
            x_scale = h["axis.x.jog-scale"]
            y_scale = h["axis.y.jog-scale"]
            if x_scale and y_scale:
                if not args.server:
                    cal_x = h["axis.x.cal"]
                    cal_y = h["axis.y.cal"]
                h["axis.x.jog-counts"] = self.old_counts_x + int(offset_x / x_scale * cal_x)
                h["axis.y.jog-counts"] = self.old_counts_y + int(offset_y / y_scale * cal_y)


class Window(QMainWindow):
    def __init__(self, app=None):
        super().__init__()
        self.video = args.video
        if args.camera and args.camera.startswith("rtsp://"):
            self.video = args.camera
        elif args.video == -1:
            for index in range(9):
                if os.path.exists(f"/sys/class/video4linux/video{index}/name"):
                    name = open(f"/sys/class/video4linux/video{index}/name").read().strip()
                    if args.camera in name:
                        self.video = index
                        break

        self.options = {
            "width": args.width,
            "height": args.height,
            "width_source": args.width,
            "height_source": args.height,
            "scale": args.scale,
            "zoom": 1.0,
            "mode": "move",
            "view": "normal",
            "points": [],
            "edges": [],
            "touch": None,
            "action": "",
        }

        self.setWindowTitle("CamJog")
        if args.xid:
            from qtvcp.lib import xembed

            window = xembed.reparent_qt_to_x11(self, args.xid)
            forward = os.environ.get("AXIS_FORWARD_EVENTS_TO", None)
            if forward:
                xembed.XEmbedForwarding(window, forward)

        if args.rotate:
            sub_layout = QHBoxLayout()
            layout = QVBoxLayout()
            self.options["width"] = args.height
            self.options["height"] = args.width
        else:
            sub_layout = QVBoxLayout()
            layout = QHBoxLayout()

        self.main = QWidget()
        self.setCentralWidget(self.main)
        self.main.setLayout(layout)
        layout.setContentsMargins(0, 0, 0, 0)

        setup_layout = QVBoxLayout()
        info_layout = QVBoxLayout()

        self.view_mode = QComboBox()
        self.view_mode.activated.connect(self.set_view)
        setup_layout.addWidget(self.view_mode)

        for view in ("normal", "gray", "edge", "contours"):
            self.view_mode.addItem(view)

        self.zoom_label = QLabel("1.0")
        setup_layout.addWidget(self.zoom_label)

        self.touch_mode = QComboBox()
        self.touch_mode.activated.connect(self.set_mode)
        setup_layout.addWidget(self.touch_mode)

        for mode in ("move", "goto", "touch", "edges"):
            self.touch_mode.addItem(mode)

        button_zero = QPushButton("set Zero")
        button_zero.clicked.connect(self.set_zero)
        setup_layout.addWidget(button_zero)

        button_to_zero = QPushButton("go Zero")
        button_to_zero.clicked.connect(self.go_to_zero)
        setup_layout.addWidget(button_to_zero)

        button_clear = QPushButton("Clear")
        button_clear.clicked.connect(self.clear_cb)
        setup_layout.addWidget(button_clear)

        self.overwrites = {}
        for overwrite in ("feed-override", "rapid-override", "spindle.0.override", "max-velocity"):
            self.overwrites[overwrite] = QLabel(overwrite)
            # setup_layout.addWidget(self.overwrites[overwrite])
            info_layout.addWidget(self.overwrites[overwrite])

        self.video_img = MyImage(self)

        layout.addWidget(self.video_img)
        layout.addLayout(sub_layout)

        sub_layout.addLayout(setup_layout)
        sub_layout.addLayout(info_layout)

        signal.signal(signal.SIGTERM, self.shutdown)
        signal.signal(signal.SIGINT, self.shutdown)

        if args.fullscreen:
            self.showFullScreen()
        self.show()

        print("camjog: starting camera thread")
        self.camera = CameraThread(self.video, self.options)
        self.camera.image.connect(self.update_image)
        self.camera.start()

        if args.device:
            print("camjog: starting serial thread")
            self.serial = SerialThread()
            self.serial.start()

        self.timer = QTimer()
        self.timer.timeout.connect(self.runTimer)
        self.timer.start(100)

    def shutdown(self, signum=None, stack_frame=None):
        print("INFO: camjog Interrupted")
        self.camera.stop()
        sys.exit(0)

    def resizeEvent(self, event):
        print("Window has been resized")
        QMainWindow.resizeEvent(self, event)

    def clear_cb(self, w):
        self.options["points"] = []
        self.options["edges"] = []
        self.options["touch"] = None
        self.camera.stop_capture()
        self.camera = CameraThread(self.video, self.options)
        self.camera.image.connect(self.update_image)
        self.camera.start()

    def exit(self):
        self.camera.stop_capture()

    def set_zero(self, _idx):
        gcode = {"name": "mdi", "gcode": f"G92 X{offset_x} Y{offset_y}"}
        print("mdi zero", gcode)
        ret = hal.rcall(json.dumps(gcode).encode())
        print("mdi ret", ret)

    def go_to_zero(self, _idx):
        gcode = {"name": "mdi", "gcode": f"G90 G0 X{offset_x} Y{offset_y}"}
        print("mdi zero", gcode)
        ret = hal.rcall(json.dumps(gcode).encode())
        print("mdi ret", ret)

    def set_mode(self, _idx):
        mode = self.touch_mode.currentText()
        self.options["mode"] = mode
        if mode == "edges" or mode == "touch":
            self.options["touch"] = None
            self.options["points"] = []

    def set_view(self, _idx):
        self.options["view"] = self.view_mode.currentText()

    def convert_to_cam(self, point):
        x = point[0]
        y = point[1]
        s = self.options["scale"]
        w = int(self.options["width"] * s)
        h = int(self.options["height"] * s)
        z = self.options["zoom"]
        cx = w // 2
        cy = h // 2

        # zoom
        x = x - (x - cx) + (x - cx) // z
        y = y - (y - cy) + (y - cy) // z

        # scale
        offset_x = int((x - cx) // s)
        offset_y = int((y - cy) // s)
        return (offset_x, offset_y)

    def convert_to_screen(self, point):
        s = self.options["scale"]
        z = self.options["zoom"]
        cx = self.options["width"] / 2
        cy = self.options["height"] / 2
        return (int((point[0] + cx) * s * z), int((point[1] + cy) * s * z))

    def update_image(self, frame):
        try:
            if args.rotate:
                frame = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)

            if self.options["view"] == "edge":
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                frame = cv2.Canny(gray, 70, 135)

            elif self.options["view"] == "contours":
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                gray = cv2.bilateralFilter(gray, 9, 75, 75)
                edges = cv2.Canny(gray, 70, 135)
                contours, hierarchy = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

                for cnt in contours:
                    approx = cv2.approxPolyDP(cnt, 0.009 * cv2.arcLength(cnt, True), True)
                    cv2.drawContours(frame, [approx], 0, (0, 0, 255), 1)

                """
                corners = cv2.goodFeaturesToTrack(edges, 4, .8, 100)
                offset = 25
                for corner in corners:
                    x,y = corner.ravel()
                    cv2.circle(frame,(x, y), 5, (36, 255, 12), -1)
                    x, y = int(x), int(y)
                    cv2.rectangle(frame, (x - offset, y - offset), (x + offset, y + offset), (36, 255, 12), 1)
                """

            elif self.options["view"] == "gray":
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            s = self.options["scale"]
            z = self.options["zoom"]
            w = self.options["width"]
            h = self.options["height"]
            cx = w // 2
            cy = h // 2

            # scale image
            nw = int(w * s * z)
            nh = int(h * s * z)
            frame = cv2.resize(frame, (nw, nh), interpolation=cv2.INTER_LINEAR)

            # draw center lines
            cv2.line(frame, (0, nh // 2), (nw, nh // 2), (255, 0, 0), 1)
            cv2.line(frame, (nw // 2, 0), (nw // 2, nh), (255, 0, 0), 1)

            # draw points
            last_point = None
            for pn, point in enumerate(self.options["points"]):
                point = self.convert_to_screen(point)
                cv2.circle(frame, point, 10, (0, 255, 0), 2)
                if last_point is not None:
                    cv2.line(frame, last_point, point, (0, 255, 0), 2)
                last_point = point

            if len(self.options["points"]) == 3:
                self.options["edges"] = self.options["points"]
            elif len(self.options["points"]) == 4:
                self.options["edges"] = self.options["points"] + self.options["points"][:1]
            else:
                self.options["edges"] = []

            if self.options["edges"]:
                # create polygon
                polygon = []
                for point in self.options["edges"]:
                    point = self.convert_to_screen(point)
                    polygon.append(point)

                # check polygon direction
                last_point = polygon[0]
                point = polygon[1]
                center = line_center_2d(last_point, point)
                angle = angle_of_line(last_point, point)
                ap_x = center[0] + 1 * math.sin(angle)
                ap_y = center[1] - 1 * math.cos(angle)
                aoff = 0.0
                if is_inside_polygon(polygon, (ap_x, ap_y)):
                    aoff = math.pi

                # calc offsets and vectors
                radius = 40
                last_point = None
                for point in polygon:
                    cv2.circle(frame, point, 10, (0, 0, 255), 2)
                    if last_point is not None:
                        cv2.line(frame, last_point, point, (0, 0, 255), 2)

                        center = line_center_2d(last_point, point)
                        cv2.circle(frame, (int(center[0]), int(center[1])), 10, (0, 0, 255), 2)

                        angle = angle_of_line(last_point, point) + aoff
                        agrid = int(((angle * 180 / math.pi) + 45) / 90) * 90
                        # print(agrid)

                        ap_x = center[0] + radius * math.sin(agrid * math.pi / 180.0)
                        ap_y = center[1] - radius * math.cos(agrid * math.pi / 180.0)

                        ap2_x = center[0] + -radius * math.sin(agrid * math.pi / 180.0)
                        ap2_y = center[1] - -radius * math.cos(agrid * math.pi / 180.0)

                        cv2.line(frame, (int(ap_x), int(ap_y)), (int(ap2_x), int(ap2_y)), (0, 0, 255), 3)

                    last_point = point

            if self.options["touch"]:
                point = self.convert_to_screen(self.options["touch"])
                cv2.circle(frame, point, 10, (0, 255, 255), 2)

            # center image
            offset_x = int(((cx * z) - cx) * s)
            offset_y = int(((cy * z) - cy) * s)
            frame = frame[offset_y : offset_y + int(h * s), offset_x : offset_x + int(w * s)]
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            image = QImage(frame, frame.shape[1], frame.shape[0], QImage.Format_RGB888)
            self.video_img.setPixmap(QPixmap.fromImage(image))
        except Exception as err:
            print("ERROR: UPDATE IMAGE: ", err)

    def runTimer(self):
        for overwrite in ("feed-override", "rapid-override", "spindle.0.override", "max-velocity"):
            self.overwrites[overwrite].setText(f"{overwrite}: {h[f'{overwrite}.value']}")


class SerialThread(QThread):
    def __init__(self):
        super().__init__()
        self.serial = serial.Serial(args.device, args.baud, timeout=0.1)

    def run(self):
        while True:
            line = self.serial.readline()
            if line and line.startswith(b"J:"):
                parts = line.decode().split(":")
                _prefix, enc0, enc1, enc2, enc3, enc4, sw = parts
                if int(enc0):
                    h["axis.x.jog-counts"] += int(enc0)

                for idx, overwrite in enumerate(("feed-override", "rapid-override", "spindle.0.override", "max-velocity")):
                    h[f"{overwrite}.counts"] += int(parts[idx + 2])

                if int(sw) != h["sw1"]:
                    h["sw1"] = int(sw)
                    h["sw1-not"] = 1 - int(sw)


class CameraThread(QThread):
    image = pyqtSignal(np.ndarray)

    def __init__(self, device, options):
        super().__init__()
        self.device = device
        self.options = options
        self.width = options["width"]
        self.height = options["height"]
        self.width_source = options["width_source"]
        self.height_source = options["height_source"]
        self.mode = options.get("view", "normal")
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


if __name__ == "__main__":
    app = QApplication(sys.argv)
    Window(app=app)
    ret = app.exec_()
    sys.exit(ret)
