#!/usr/bin/env python3
#
#
"""

EMBED_TAB_NAME=robojog
EMBED_TAB_COMMAND=halcmd loadusr -Wn robojog /data2/src/ICE40-2023/serial-tx/riocore/robot-jog.py --xid {XID} --joints 6

net robojog_0 <= robojog.joint.0.jog-counts
net robojog_0 => joint.0.jog-counts
setp joint.0.jog-vel-mode 0
setp joint.0.jog-enable 1
setp joint.0.jog-scale 0.01

net robojog_1 <= robojog.joint.1.jog-counts
net robojog_1 => joint.1.jog-counts
setp joint.1.jog-vel-mode 0
setp joint.1.jog-enable 1
setp joint.1.jog-scale 0.01

net robojog_2 <= robojog.joint.2.jog-counts
net robojog_2 => joint.2.jog-counts
setp joint.2.jog-vel-mode 0
setp joint.2.jog-enable 1
setp joint.2.jog-scale 0.01

net robojog_3 <= robojog.joint.3.jog-counts
net robojog_3 => joint.3.jog-counts
setp joint.3.jog-vel-mode 0
setp joint.3.jog-enable 1
setp joint.3.jog-scale 0.01


net j0pos-fb => robojog.joint.0.position
net j1pos-fb => robojog.joint.1.position
net j2pos-fb => robojog.joint.2.position
net j3pos-fb => robojog.joint.3.position
net j4pos-fb => robojog.joint.4.position
net j5pos-fb => robojog.joint.5.position

setp robojog.joint.0.scale 100.0
setp robojog.joint.1.scale 100.0
setp robojog.joint.2.scale 100.0
setp robojog.joint.3.scale 100.0
setp robojog.joint.4.scale 100.0



"""

import math
import argparse
import glob
import os
import sys
import time
import traceback
from functools import partial

from PyQt5.QtCore import Qt, QTimer, QThread, pyqtSignal
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtWidgets import (
    QLineEdit,
    QApplication,
    QCheckBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QPushButton,
    QSlider,
    QVBoxLayout,
    QWidget,
    QTabWidget,
)

JOINTS = 6

try:
    import hal
    h = hal.component("robojog")
    for joint in range(JOINTS):
        h.newpin(f"joint.{joint}.jog-counts", hal.HAL_S32, hal.HAL_OUT)
        h.newpin(f"joint.{joint}.position", hal.HAL_FLOAT, hal.HAL_IN)
        h.newpin(f"joint.{joint}.scale", hal.HAL_FLOAT, hal.HAL_IN)
        h[f"joint.{joint}.jog-counts"] = 0
    h.ready()
    no_hal = False
except Exception:
    no_hal = True
    h = {}
    for joint in range(JOINTS):
        h[f"joint.{joint}.jog-counts"] = 0
        h[f"joint.{joint}.position"] = 0
        h[f"joint.{joint}.scale"] = 10.0


class WinForm(QWidget):
    def __init__(self, parent=None):
        super(WinForm, self).__init__(parent)
        parser = argparse.ArgumentParser()
        parser.add_argument("--xid", help="parent x window id", type=int)
        parser.add_argument("--joints", help="number of joints", type=int, default=JOINTS)
        args = parser.parse_args()
        self.setMinimumWidth(400)
        self.setMinimumHeight(300)
        self.joints = args.joints

        self.setWindowTitle("RoboJog")
        if args.xid:
            from qtvcp.lib import xembed

            window = xembed.reparent_qt_to_x11(self, args.xid)
            forward = os.environ.get('AXIS_FORWARD_EVENTS_TO', None)
            if forward:
                xembed.XEmbedForwarding(window, forward)

        layout = QVBoxLayout()
        self.setLayout(layout)

        def slide_stop(joint):
            #print("stop update")
            self.jdata[joint]["active"] = False
            self.jdata[joint]["last"] = self.jdata[joint]["slider"].value()

        def slide_start(joint):
            #print("start update")
            self.jdata[joint]["active"] = True

        def slide_move(joint, pos):
            #print(f"joint.{joint}.jog-counts", int(pos - self.jdata[joint]["last"]))
            h[f"joint.{joint}.jog-counts"] += int(pos - self.jdata[joint]["last"])
            self.jdata[joint]["last"] = pos


        self.jdata = []
        for joint in range(self.joints):
            jdata = {
                "last": 0,
                "active": True,
                "label": None,
                "slider": None,
            }
            #print(joint, h[f"joint.{joint}.scale"])
            jdata["label"] = QLabel(f"j{joint}: --")
            jdata["slider"] = QSlider(Qt.Horizontal)
            jdata["slider"].setFixedWidth(250)
            jdata["slider"].setMinimum(int(-45 * abs(h[f"joint.{joint}.scale"])))
            jdata["slider"].setMaximum(int(45 * abs(h[f"joint.{joint}.scale"])))
            jdata["slider"].setSingleStep(1)
            jdata["slider"].sliderPressed.connect(partial(slide_stop, joint))
            jdata["slider"].sliderReleased.connect(partial(slide_start, joint))
            jdata["slider"].sliderMoved.connect(partial(slide_move, joint))

            layout.addWidget(jdata["label"])
            layout.addWidget(jdata["slider"])

            self.jdata.append(jdata)

        self.timer = QTimer()
        self.timer.timeout.connect(self.runTimer)
        self.timer.start(300)

    def runTimer(self):
        for joint in range(self.joints):
            jdata = self.jdata[joint]
            #print(joint, jdata)
            pos = h[f"joint.{joint}.position"]
            jdata["label"].setText(f"J0: {pos:0.3f}")
            if self.jdata[joint]["active"]:
                jdata["slider"].setValue(int(pos * abs(h[f"joint.{joint}.scale"])))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    form = WinForm()
    form.show()
    sys.exit(app.exec_())
