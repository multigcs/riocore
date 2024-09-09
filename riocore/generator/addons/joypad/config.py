import os
import fcntl
import glob
from functools import partial

from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import (
    QComboBox,
    QDialog,
    QLineEdit,
    QDialogButtonBox,
    QGridLayout,
    QLabel,
    QVBoxLayout,
    QPushButton,
    QHBoxLayout,
    QWidget,
)

from riocore.widgets import MyStandardItem


def info():
    return {
        "title": "joypad",
        "url": "",
        "comment": "joypad support",
    }


def device_get_name(device_path):
    try:
        f = os.open(device_path, os.O_RDWR)
    except os.error:
        return
    try:
        r = fcntl.ioctl(f, (0x80004506 - 2**32) | (1024 << 16), "\0" * 1024)
        return r.decode("utf-8", errors="replace").rstrip("\0")
    except os.error:
        return


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


def load_tree(parent, tree_lcnc):
    def wiz2_joypad(selected_device):
        import linux_event

        device_events = linux_event.InputDevice(selected_device)

        def wiz_select(action, clicked):
            selected_label.setText(action)

        def wiz_runTimer():
            action = selected_label.text()
            while device_events.readable():
                ev = device_events.read_event()
                if ev.type == "EV_SYN":
                    continue
                elif ev.type == "EV_SND":
                    continue
                elif ev.type == "EV_MSC":
                    continue
                elif ev.type == "EV_LED":
                    continue

                halname = ev.code.lower().replace("_", "-")
                if ALL_ACTIONS[action] == "axis" and halname.startswith("abs"):
                    actions[action].setText(halname)
                elif ALL_ACTIONS[action] == "button" and halname.startswith("btn"):
                    actions[action].setText(halname)

        dialog = QDialog()
        dialog.setWindowTitle("select device")
        # dialog.setStyleSheet(STYLESHEET)

        dialog.buttonBox = QDialogButtonBox(QDialogButtonBox.Ok)
        dialog.buttonBox.accepted.connect(dialog.accept)

        dialog.layout = QGridLayout()
        selected_label = QLabel("x")
        dialog.layout.addWidget(selected_label, 0, 0)

        actions = {}
        row = 1
        for action, atype in ALL_ACTIONS.items():
            actions[action] = QLineEdit()
            axis_x_button = QPushButton(action)
            cb = partial(wiz_select, action)
            axis_x_button.clicked.connect(cb)
            dialog.layout.addWidget(actions[action], row, 0)
            dialog.layout.addWidget(axis_x_button, row, 1)
            row += 1

        dialog.layout.addWidget(dialog.buttonBox)
        dialog.setLayout(dialog.layout)

        timer = QTimer()
        timer.timeout.connect(wiz_runTimer)
        timer.start(300)

        if dialog.exec():
            for action, atype in ALL_ACTIONS.items():
                halname = actions[action].text()
                if halname:
                    parent.config["linuxcnc"]["joypad"][action] = halname
            parent.config["linuxcnc"]["joypad"]["name"] = selected_device
            parent.load_tree("/LinuxCNC/AddOn's/Joypad/")
            parent.display()

        timer.stop()

    def wiz_joypad(button_wizard):
        devices = []
        for device_path in glob.glob("/dev/input/event*"):
            name = device_get_name(device_path)
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
            wiz2_joypad(selected_device)

    def add_joypad(widget):
        if not parent.config["linuxcnc"].get("joypad"):
            parent.config["linuxcnc"]["joypad"] = {
                "enable": False,
                "name": "Joystick",
            }
            parent.load_tree()
            parent.display()

    bitem = MyStandardItem()
    tree_lcnc.appendRow(
        [
            MyStandardItem("Joypad", help_text="LinuxCNC Joypad-Setup"),
            bitem,
        ]
    )

    buttons_layout = QHBoxLayout()
    buttons_layout.setContentsMargins(0, 0, 0, 0)
    buttons_widget = QWidget()
    buttons_widget.setLayout(buttons_layout)

    if "joypad" not in parent.config["linuxcnc"]:
        button_add = QPushButton("add")
        button_add.clicked.connect(add_joypad)
        button_add.setMaximumSize(button_add.sizeHint())
        buttons_layout.addWidget(button_add)
    button_wizard = QPushButton("wizard")
    button_wizard.clicked.connect(wiz_joypad)
    button_wizard.setMaximumSize(button_wizard.sizeHint())
    buttons_layout.addWidget(button_wizard)
    buttons_layout.addStretch()
    parent.treeview.setIndexWidget(bitem.index(), buttons_widget)

    tree_lcncjoypad = tree_lcnc.child(tree_lcnc.rowCount() - 1)
    joypad_config = parent.config["linuxcnc"].get("joypad")
    if joypad_config:
        joypad_buttons = ["btn-base", "btn-base2", "btn-top", "btn-top2"]
        joypad_axis = ["abs-x", "abs-y", "abs-z", "abs-rz"]

        options = {
            "enable": {"type": bool, "default": False},
            "name": {"type": str},
        }
        for action, atype in ALL_ACTIONS.items():
            if atype == "button":
                options[action] = {"type": "select", "options": joypad_buttons}
            else:
                options[action] = {"type": "select", "options": joypad_axis}

        for key, var_setup in options.items():
            aitem = MyStandardItem()
            tree_lcncjoypad.appendRow(
                [
                    MyStandardItem(key.title()),
                    aitem,
                ]
            )
            parent.treeview.setIndexWidget(aitem.index(), parent.edit_item(joypad_config, key, var_setup))
