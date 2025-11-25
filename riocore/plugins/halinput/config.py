import glob
import os
import sys
from functools import partial

from PyQt5.QtCore import QTimer, pyqtSignal
from PyQt5.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QGridLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
)

plugin_path = os.path.dirname(__file__)


if sys.platform == "linux":
    import fcntl


def info():
    return {
        "title": "joypad",
        "url": "",
        "comment": "joypad support",
    }


def device_get_name(device_path):
    try:
        f = os.open(device_path, os.O_RDWR)
    except OSError:
        return None
    try:
        r = fcntl.ioctl(f, (0x80004506 - 2**32) | (1024 << 16), "\0" * 1024)
        return r.decode("utf-8", errors="replace").rstrip("\0")
    except OSError:
        return None


ALL_ACTIONS = {
    "x": "axis",
    "y": "axis",
    "z": "axis",
    "a": "axis",
    "b": "axis",
    "c": "axis",
    "slow": "button",
    "medium": "button",
    "fast": "button",
}


class ClickableLineEdit(QLineEdit):
    clicked = pyqtSignal()

    def mousePressEvent(self, event):
        self.clicked.emit()
        super().mousePressEvent(event)


class config:
    def __init__(self, instance, styleSheet=None):
        self.instance = instance
        self.plugin_setup = instance.plugin_setup

    def wiz2_joypad(self, selected_device):
        import linux_event

        device_events = linux_event.InputDevice(selected_device)

        def wiz_select(action, clicked=None):
            selected_label.setText(action)
            for item in actions:
                actions[item].setStyleSheet("")
            actions[action].setStyleSheet("QLineEdit {background-color: rgb(255, 200, 200);}")

        def wiz_runTimer():
            action = selected_label.text()
            while device_events.readable():
                ev = device_events.read_event()
                if ev.type == "EV_SYN" or ev.type == "EV_SND" or ev.type == "EV_MSC" or ev.type == "EV_LED":
                    continue

                halname = ev.code.lower().replace("_", "-")
                if (ALL_ACTIONS[action] == "axis" and halname.startswith("abs")) or (ALL_ACTIONS[action] == "button" and halname.startswith("btn")):
                    actions[action].setText(halname)

        dialog = QDialog()
        dialog.setWindowTitle("select device")
        # dialog.setStyleSheet(STYLESHEET)

        dialog.buttonBox = QDialogButtonBox(QDialogButtonBox.Ok)
        dialog.buttonBox.accepted.connect(dialog.accept)

        dialog.layout = QGridLayout()
        selected_label = QLabel("x")
        dialog.layout.addWidget(selected_label, 0, 0)

        for key, value in self.instance.OPTIONS.items():
            if key not in self.plugin_setup:
                self.plugin_setup[key] = value["default"]

        actions = {}
        row = 1
        for action in ALL_ACTIONS:
            actions[action] = ClickableLineEdit()
            actions[action].setText(self.plugin_setup.get(action, ""))
            button = QPushButton(action)
            cb = partial(wiz_select, action)
            actions[action].clicked.connect(cb)
            button.clicked.connect(cb)
            dialog.layout.addWidget(actions[action], row, 0)
            dialog.layout.addWidget(button, row, 1)
            row += 1

        wiz_select("x")

        dialog.layout.addWidget(dialog.buttonBox)
        dialog.setLayout(dialog.layout)

        timer = QTimer()
        timer.timeout.connect(wiz_runTimer)
        timer.start(300)

        if dialog.exec():
            for action in ALL_ACTIONS:
                halname = actions[action].text()
                if halname:
                    self.plugin_setup[action] = halname
            self.plugin_setup["joypad_name"] = selected_device

        timer.stop()

    def wiz_joypad(self):
        devices = []
        for device_path in glob.glob("/dev/input/event*"):
            name = device_get_name(device_path)
            if name:
                devices.append(name)

        dialog = QDialog()
        dialog.setWindowTitle("select device")
        # dialog.setStyleSheet(STYLESHEET)

        dialog.buttonBox = QDialogButtonBox(QDialogButtonBox.Ok)
        dialog.buttonBox.accepted.connect(dialog.accept)

        dialog.layout = QVBoxLayout()
        combo_devices = QComboBox()
        for device_name in devices:
            combo_devices.addItem(device_name)
        dialog.layout.addWidget(combo_devices)

        dialog.layout.addWidget(dialog.buttonBox)
        dialog.setLayout(dialog.layout)

        if dialog.exec():
            selected_device = combo_devices.currentText()
            self.wiz2_joypad(selected_device)

    def run(self):
        self.wiz_joypad()


if __name__ == "__main__":
    import json
    import sys

    from PyQt5.QtWidgets import QApplication

    app = QApplication(sys.argv)

    class mock_instance:
        def __init__(self):
            self.instances_name = "halinput1"
            self.plugin_setup = {}
            self.OPTIONS = {
                "joypad_name": {
                    "type": str,
                    "default": "Joystick",
                },
                "slow": {
                    "type": str,
                    "default": "btn-top2",
                },
                "medium": {
                    "type": str,
                    "default": "btn-base",
                },
                "fast": {
                    "type": str,
                    "default": "btn-pinkie",
                },
            }
            for axis, default in {
                "x": "abs-x",
                "y": "-abs-y",
                "z": "-abs-rz",
                "a": "",
                "b": "",
                "c": "",
            }.items():
                self.OPTIONS[axis] = {
                    "type": str,
                    "default": default,
                }

    instance = mock_instance()
    config_gui = config(instance)
    config_gui.run()
    print(json.dumps(instance.plugin_setup, indent=4))
