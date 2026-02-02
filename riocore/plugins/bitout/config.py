import os
import sys

from PyQt5.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QLabel,
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
        dialog.setWindowTitle("select halpin")
        dialog.buttonBox = QDialogButtonBox(QDialogButtonBox.Ok)
        dialog.buttonBox.accepted.connect(dialog.accept)

        net = self.plugin_setup.get("signals", {}).get("bit", {}).get("net", "")
        options = []
        options.append(("Spindle-On", "spindle.0.on"))
        options.append(("Spindle-Forward", "spindle.0.forward"))
        options.append(("Spindle-Reverse", "spindle.0.reverse"))
        options.append(("Coolant-Mist", "iocontrol.0.coolant-mist"))
        options.append(("Coolant-Flood", "iocontrol.0.coolant-flood"))
        options.append(("Machine is on", "halui.machine.is-on"))

        dialog.layout = QVBoxLayout()
        dialog.layout.addWidget(QLabel("Easy quick selection for the most frequently used functions\n"))
        dialog.layout.addWidget(QLabel("Function"))
        halpin = QComboBox()
        halpin.addItem("")
        for idx, option in enumerate(options):
            halpin.addItem(f"{option[0]} ({option[1]}")
            if net == option[1]:
                halpin.setCurrentIndex(idx + 1)

        dialog.layout.addWidget(halpin)
        dialog.layout.addWidget(dialog.buttonBox)
        dialog.setLayout(dialog.layout)

        if dialog.exec():
            halpin = halpin.currentText()
            if "(" in halpin:
                halpin = halpin.currentText().split("(")[1].split(")")[0]
            if halpin:
                if "signals" not in self.plugin_setup:
                    self.self.plugin_setup["signals"] = {}
                if "bit" not in self.plugin_setup["signals"]:
                    self.self.plugin_setup["signals"]["bit"] = {}
            self.plugin_setup["signals"]["bit"]["net"] = halpin


if __name__ == "__main__":
    import json
    import sys

    from PyQt5.QtWidgets import QApplication

    app = QApplication(sys.argv)

    class mock_instance:
        def __init__(self):
            self.instances_name = "home-z"
            self.plugin_setup = {"signals": {"bit": {"net": "joint.2.home-sw-in"}}}

    instance = mock_instance()
    config_gui = config(instance)
    config_gui.run()
    print(json.dumps(instance.plugin_setup, indent=4))
