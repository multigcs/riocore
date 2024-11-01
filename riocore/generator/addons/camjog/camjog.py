#!/usr/bin/env python3
#
#
"""

EMBED_TAB_NAME=CamJog
EMBED_TAB_COMMAND=halcmd loadusr -Wn camjog /data2/src/ICE40-2023/serial-tx/riocore/camjog.py --xid {XID} --camera USB2.0 --width 640 --height 480 --scale 1.5

net camjog_x <= camjog.axis.x.jog-counts
net camjog_x => joint.0.jog-counts
net camjog_x => axis.x.jog-counts
setp joint.0.jog-vel-mode 0
setp joint.0.jog-enable 1
setp joint.0.jog-scale 0.01
setp axis.x.jog-vel-mode 0
setp axis.x.jog-enable 1
setp axis.x.jog-scale 0.15


net camjog_y <= camjog.axis.y.jog-counts
net camjog_y => joint.1.jog-counts
net camjog_y => axis.y.jog-counts
setp joint.1.jog-vel-mode 0
setp joint.1.jog-enable 1
setp joint.1.jog-scale 0.01
setp axis.y.jog-vel-mode 0
setp axis.y.jog-enable 1
setp axis.y.jog-scale -0.15



"""

import math
import argparse
import os
import sys
from functools import partial

from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

import numpy as np
import cv2

try:
    import hal

    h = hal.component("camjog")
    h.newpin("axis.x.jog-counts", hal.HAL_S32, hal.HAL_OUT)
    h.newpin("axis.y.jog-counts", hal.HAL_S32, hal.HAL_OUT)
    h.ready()
    no_hal = False
except Exception:
    no_hal = True

TWO_PI = math.pi * 2


def line_center_2d(p_1, p_2):
    """gets the center point between 2 points in 2D."""
    center_x = (p_1[0] + p_2[0]) / 2
    center_y = (p_1[1] + p_2[1]) / 2
    return (center_x, center_y)


def angle_of_line(p_1, p_2):
    """gets the angle of a single line."""
    return math.atan2(p_2[1] - p_1[1], p_2[0] - p_1[0])


def angle_2d(p_1, p_2):
    """gets the angle of a single line (2nd version)."""
    theta1 = math.atan2(p_1[1], p_1[0])
    theta2 = math.atan2(p_2[1], p_2[0])
    dtheta = theta2 - theta1
    while dtheta > math.pi:
        dtheta -= TWO_PI
    while dtheta < -math.pi:
        dtheta += TWO_PI
    return dtheta


def is_inside_polygon(polygon, point):
    """checks if a point is inside an polygon."""
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
            if self.parent.options["zoom"] < 1.0:
                self.parent.options["zoom"] = 1.0
        else:
            if self.parent.options["zoom"] < 10.0:
                self.parent.options["zoom"] += 0.1

        self.parent.zoom_label.setText(f"{self.parent.options['zoom']:0.1f}")

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.new_x = event.pos().x()
            self.new_y = event.pos().y()
            self.old_x = self.new_x
            self.old_y = self.new_y
            self.old_counts_x = h["axis.x.jog-counts"]
            self.old_counts_y = h["axis.y.jog-counts"]

            (offset_x, offset_y) = self.parent.convert_to_cam((self.new_x, self.new_y))

            if self.parent.options["mode"] == "goto":
                h["axis.x.jog-counts"] += offset_x
                h["axis.y.jog-counts"] += offset_y

            elif self.parent.options["mode"] == "touch":
                self.parent.options["points"] = []
                self.parent.options["touch"] = (offset_x, offset_y)
                self.parent.options["mode"] = "edges"
                self.parent.info_label.setText("edges")

            elif self.parent.options["mode"] == "edges":
                if len(self.parent.options["points"]) > 3:
                    self.parent.options["points"] = []
                self.parent.options["points"].append((offset_x, offset_y))

    def mouseReleaseEvent(self, event):
        pass

    def mouseMoveEvent(self, event):
        if self.parent.options["mode"] == "move":
            diff_x = self.old_x - event.pos().x()
            diff_y = self.old_y - event.pos().y()
            s = self.parent.options["scale"]
            z = self.parent.options["zoom"]
            h["axis.x.jog-counts"] = self.old_counts_x + int(diff_x / z / s)
            h["axis.y.jog-counts"] = self.old_counts_y + int(diff_y / z / s)


class WinForm(QWidget):
    def __init__(self, parent=None):
        super(WinForm, self).__init__(parent)
        parser = argparse.ArgumentParser()
        parser.add_argument("--xid", help="parent x window id", type=int)
        parser.add_argument("--video", help="video device id", type=int, default=-1)
        parser.add_argument("--camera", help="video device name", type=str, default="")
        parser.add_argument("--width", help="video device width", type=int, default=640)
        parser.add_argument("--height", help="video device height", type=int, default=480)
        parser.add_argument("--scale", help="scale image", type=float, default=1.0)
        args = parser.parse_args()

        if args.video == -1:
            for index in range(9):
                if os.path.exists(f"/sys/class/video4linux/video{index}/name"):
                    name = open(f"/sys/class/video4linux/video{index}/name", "r").read().strip()
                    if args.camera in name:
                        args.video = index
                        break

        self.options = {
            "width": args.width,
            "height": args.height,
            "scale": args.scale,
            "zoom": 1.0,
            "mode": "move",
            "view": "normal",
            "points": [],
            "edges": [],
            "touch": None,
            "action": "",
        }

        s = self.options["scale"]
        self.setMinimumWidth(int(args.width * s) + 50)
        self.setMinimumHeight(int(args.height * s) + 100)

        # self.setFixedWidth(int(args.width * s) + 50)
        # self.setFixedWidth(int(args.height * s) + 100)

        self.setWindowTitle("CamJog")
        if args.xid:
            from qtvcp.lib import xembed

            window = xembed.reparent_qt_to_x11(self, args.xid)
            forward = os.environ.get("AXIS_FORWARD_EVENTS_TO", None)
            if forward:
                xembed.XEmbedForwarding(window, forward)

        layout = QVBoxLayout()
        self.setLayout(layout)

        setup_container = QWidget()
        setup_layout = QHBoxLayout(setup_container)
        layout.addWidget(setup_container)

        for view in ("normal", "gray", "edge", "contours"):
            button_view = QPushButton(view.title())
            button_view.clicked.connect(partial(self.change_view, view))
            setup_layout.addWidget(button_view)
        setup_layout.addStretch()

        self.info_label = QLabel("---")
        setup_layout.addWidget(self.info_label)

        self.zoom_label = QLabel("1.0")
        setup_layout.addWidget(self.zoom_label)

        ctrl_container = QWidget()
        ctrl_layout = QHBoxLayout(ctrl_container)
        layout.addWidget(ctrl_container)

        for mode in ("move", "goto", "touch", "edges"):
            button_mode = QPushButton(mode.title())
            button_mode.clicked.connect(partial(self.change_mode, mode))
            ctrl_layout.addWidget(button_mode)
        ctrl_layout.addStretch()

        button_clear = QPushButton("Clear")
        button_clear.clicked.connect(self.clear_cb)
        ctrl_layout.addWidget(button_clear)

        self.video_img = MyImage(self)
        self.video_img.setFixedWidth(int(args.width * s))
        self.video_img.setFixedHeight(int(args.height * s))

        layout.addWidget(self.video_img)
        layout.addStretch()

        self.video = args.video
        self.camera = CameraThread(self.video, self.options)
        self.camera.image.connect(self.update_image)
        self.camera.start()

    def clear_cb(self, w):
        self.options["points"] = []
        self.options["edges"] = []
        self.options["touch"] = None
        self.camera.stop_capture()
        self.camera = CameraThread(self.video, self.options)
        self.camera.image.connect(self.update_image)
        self.camera.start()

    def change_mode(self, mode):
        self.options["mode"] = mode
        if mode == "edges" or mode == "touch":
            self.options["touch"] = None
            self.options["points"] = []

    def change_view(self, view):
        self.options["view"] = view

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


class CameraThread(QThread):
    image = pyqtSignal(np.ndarray)

    def __init__(self, device, options):
        super().__init__()
        self.device = device
        self.options = options
        self.width = options["width"]
        self.height = options["height"]
        self.mode = options.get("view", "normal")
        self.capture = None

    def start_capture(self):
        self.capture = cv2.VideoCapture(self.device)
        self.capture.set(3, self.width)
        self.capture.set(4, self.height)

    def stop_capture(self):
        if self.capture:
            self.capture.release()
            self.capture = None

    def run(self):
        self.start_capture()
        while self.capture:
            ret, frame = self.capture.read()
            if ret:
                self.image.emit(frame)

    def stop(self):
        self.stop_capture()
        super().stop()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    form = WinForm()
    form.show()
    sys.exit(app.exec_())
