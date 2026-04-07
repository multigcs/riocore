#!/usr/bin/env python3
#
#

import json
import signal
import sys

from PyQt5.QtWidgets import (
    QApplication,
    QCheckBox,
    QDialog,
    QDialogButtonBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QVBoxLayout,
)


def wizard():
    wizard = QDialog()
    wizard.setWindowTitle("rio-flow")
    wizard.layout = QVBoxLayout()
    wizard.setLayout(wizard.layout)

    row = QHBoxLayout()
    label = QLabel("Axis:")
    label.setMinimumWidth(200)
    row.addWidget(label)
    axis = QLineEdit()
    axis.setText("XYZ")
    row.addWidget(axis)
    wizard.layout.addLayout(row)

    row = QHBoxLayout()
    label = QLabel("Spindle-Relay:")
    label.setMinimumWidth(200)
    row.addWidget(label)
    relay = QCheckBox()
    relay.setChecked(True)
    row.addWidget(relay)
    wizard.layout.addLayout(row)

    row = QHBoxLayout()
    label = QLabel("Spindle-PWM:")
    label.setMinimumWidth(200)
    row.addWidget(label)
    pwm = QCheckBox()
    pwm.setChecked(True)
    row.addWidget(pwm)
    wizard.layout.addLayout(row)

    dialog_buttonBox = QDialogButtonBox(QDialogButtonBox.Ok)
    dialog_buttonBox.accepted.connect(wizard.accept)
    wizard.layout.addWidget(dialog_buttonBox)

    if wizard.exec():
        return generate(axis=axis.text(), pwm=pwm.isChecked(), relay=relay.isChecked())

    exit(0)


def generate(axis="XYZ", inputs=5, pwm=True, relay=True):
    config = {
        "name": "Parport",
        "plugins": [
            {
                "type": "breakout",
                "node_type": "china-bob5x",
                "uid": "china-bob5x0",
                "pos": [240.0, 0.0],
                "rotate": 0,
                "pins": {
                    "SLOT:P1": {"pin": "parport0:DB25:P1"},
                    "SLOT:P2": {"pin": "parport0:DB25:P2"},
                    "SLOT:P3": {"pin": "parport0:DB25:P3"},
                    "SLOT:P4": {"pin": "parport0:DB25:P4"},
                    "SLOT:P5": {"pin": "parport0:DB25:P5"},
                    "SLOT:P6": {"pin": "parport0:DB25:P6"},
                    "SLOT:P7": {"pin": "parport0:DB25:P7"},
                    "SLOT:P8": {"pin": "parport0:DB25:P8"},
                    "SLOT:P9": {"pin": "parport0:DB25:P9"},
                    "SLOT:P10": {"pin": "parport0:DB25:P10"},
                    "SLOT:P11": {"pin": "parport0:DB25:P11"},
                    "SLOT:P12": {"pin": "parport0:DB25:P12"},
                    "SLOT:P13": {"pin": "parport0:DB25:P13"},
                    "SLOT:P14": {"pin": "parport0:DB25:P14"},
                    "SLOT:P15": {"pin": "parport0:DB25:P15"},
                    "SLOT:P16": {"pin": "parport0:DB25:P16"},
                    "SLOT:P17": {"pin": "parport0:DB25:P17"},
                },
            },
            {"type": "gpioout", "uid": "gpioout0", "pos": [660.0, -60.0], "signals": {"bit": {"net": "halui.machine.is-on", "setp": ""}}, "name": "enable", "pins": {"bit": {"pin": "china-bob5x0:ALL:en"}}},
            {"type": "parport", "uid": "parport0", "pos": [140.0, 130.0], "rotate": 0, "name": "pport"},
        ],
        "linuxcnc": {"ini": {"DISPLAY": {"DEFAULT_LINEAR_VELOCITY": 20.0}}},
    }

    if pwm:
        config["plugins"].append(
            {"type": "pwmgen", "pins": {"pwm": {"pin": "china-bob5x0:PWM:analog"}}, "uid": "pwmgen0", "pos": [470.0, -170.0], "signals": {"value": {"net": "spindle.0.speed-out", "setp": ""}, "enable": {"net": "spindle.0.on", "setp": ""}}, "name": "spindle", "image": "spindle500w", "rotate": 0},
        )

    if relay:
        config["plugins"].append(
            {"type": "gpioout", "pins": {"bit": {"pin": "china-bob5x0:RELAIS:out"}}, "uid": "gpioout1", "pos": [260.0, -250.0], "signals": {"bit": {"net": "spindle.0.on", "setp": ""}}, "name": "spindle-on", "image": "relay", "rotate": -90},
        )

    pos_y = -380.0 + 280.0 * len(axis)
    for axis_n, axis_name in enumerate(axis):
        config["plugins"].append(
            {
                "type": "stepgen",
                "uid": f"stepgen_j{axis_n}",
                "pos": [920.0, pos_y],
                "is_joint": True,
                "pins": {"step": {"pin": f"china-bob5x0:{axis_name}:step"}, "dir": {"pin": f"china-bob5x0:{axis_name}:dir"}},
                "joint": {"scale": -800.0, "home_search_vel": -10.0, "home_final_vel": 20.0, "min_limit": 0.0, "max_limit": 230.0, "max_velocity": 25.0, "home_latch_vel": -1.0},
                "image": "stepper",
                "axis": axis_name,
                "rotate": 0,
            },
        )
        pos_y -= 280.0

    max_inputs = 5
    input_num = 0
    pos_y = 540.0
    for axis_n, axis_name in enumerate(axis):
        if input_num < max_inputs:
            config["plugins"].append(
                {
                    "type": "gpioin",
                    "pins": {"bit": {"pin": f"china-bob5x0:OPTO:in{input_num}", "modifier": [{"type": "invert", "pos": [470.0, pos_y]}]}},
                    "uid": f"gpioin_j{axis_n}",
                    "pos": [640.0, pos_y],
                    "signals": {"bit": {"net": f"joint.{axis_n}.home-sw-in"}},
                    "name": f"home_{axis_n}",
                    "image": "proximity",
                    "rotate": 0,
                },
            )
            pos_y += 70.0
            input_num += 1

    if input_num < max_inputs:
        config["plugins"].append(
            {"type": "gpioin", "pins": {"bit": {"pin": f"china-bob5x0:OPTO:in{input_num}", "modifier": [{"type": "invert", "pos": [470.0, pos_y + 70]}]}}, "uid": "probe", "pos": [640.0, pos_y], "signals": {"bit": {"net": "motion.probe-input"}}, "name": "probe", "image": "probe", "rotate": 0},
        )
        pos_y += 150.0
        input_num += 1
    if input_num < max_inputs:
        config["plugins"].append(
            {"type": "gpioin", "pins": {"bit": {"pin": f"china-bob5x0:OPTO:in{input_num}", "modifier": [{"type": "invert", "pos": [470.0, pos_y + 70]}]}}, "uid": "estop", "pos": [640.0, pos_y], "signals": {"bit": {"net": "iocontrol.0.emc-enable-in"}}, "name": "estop_sw", "image": "estop", "rotate": 0},
        )
        pos_y += 150.0
        input_num += 1

    return config


class Window(QMainWindow):
    def __init__(self, app=None):
        super().__init__()
        print(json.dumps(wizard(), indent=4))
        exit(0)


if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    app = QApplication(sys.argv)
    Window(app=app)
    app.exec()
