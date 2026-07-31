import os
import sys

from PyQt5.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QLabel,
    QSpinBox,
    QVBoxLayout,
)

plugin_path = os.path.dirname(__file__)


class config:
    def __init__(self, instance, styleSheet=None, parent=None):
        self.instance = instance
        self.parent = parent
        self.plugin_setup = instance.plugin_setup

    def run(self):
        dialog = QDialog()
        dialog.setWindowTitle("setup pwmout")
        dialog.buttonBox = QDialogButtonBox(QDialogButtonBox.Ok)
        dialog.buttonBox.accepted.connect(dialog.accept)

        net = self.plugin_setup.get("signals", {}).get("dty", {}).get("net", "")
        scale = self.plugin_setup.get("signals", {}).get("dty", {}).get("scale", 0.005)
        options = []
        options.append(("Spindle0", "spindle.0.speed-out"))
        options.append(("Spindle1", "spindle.1.speed-out"))
        dialog.layout = QVBoxLayout()
        dialog.layout.addWidget(QLabel("Easy quick selection for the most frequently used functions\n"))


        dialog.layout.addWidget(QLabel("Function:"))
        halpin_widget = QComboBox()
        halpin_widget.addItem("")
        for idx, option in enumerate(options):
            halpin_widget.addItem(f"{option[0]} ({option[1]})")
            if net == option[1]:
                halpin_widget.setCurrentIndex(idx + 1)
        dialog.layout.addWidget(halpin_widget)

        dialog.layout.addWidget(QLabel("Max Spindle-Speed:"))
        speed_widget = QSpinBox()
        speed_widget.setMinimum(100)
        speed_widget.setMaximum(100000)
        speed_widget.setValue(int(100.0 / scale))
        dialog.layout.addWidget(speed_widget)

        dialog.layout.addWidget(dialog.buttonBox)
        dialog.setLayout(dialog.layout)

        if dialog.exec():
            halpin = halpin_widget.currentText()
            if "(" in halpin:
                halpin = halpin.split("(")[1].split(")")[0]
            if halpin:
                if "signals" not in self.plugin_setup:
                    self.plugin_setup["signals"] = {}
                if "dty" not in self.plugin_setup["signals"]:
                    self.plugin_setup["signals"]["dty"] = {}
                if "enable" not in self.plugin_setup["signals"]:
                    self.plugin_setup["signals"]["enable"] = {}
            self.plugin_setup["signals"]["dty"]["net"] = halpin
            self.plugin_setup["signals"]["enable"]["net"] = ""
            if halpin and halpin.startswith("spindle."):
                spindle_num = halpin.split(".")[1]
                scale = 100.0 / speed_widget.value()
                self.plugin_setup["signals"]["enable"]["net"] = f"spindle.{spindle_num}.on"
                self.plugin_setup["signals"]["dty"]["scale"] = scale


if __name__ == "__main__":
    import json
    import sys

    from PyQt5.QtWidgets import QApplication

    app = QApplication(sys.argv)

    class mock_instance:
        def __init__(self):
            self.instances_name = "pwm0"
            self.plugin_setup = {"signals": {
                "dty": {"net": "spindle.0.speed-out", "scale": 0.016666666},
                "enable": {"net": "spindle.0.on"},
            }}

    instance = mock_instance()
    config_gui = config(instance)
    config_gui.run()
    print(json.dumps(instance.plugin_setup, indent=4))
