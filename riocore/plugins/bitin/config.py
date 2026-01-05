import os
import sys

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QVBoxLayout,
)

plugin_path = os.path.dirname(__file__)


class config:
    def __init__(self, instance, styleSheet=None):
        self.instance = instance
        self.plugin_setup = instance.plugin_setup

    def run(self):
        dialog = QDialog()
        dialog.setWindowTitle("select halpin")
        dialog.buttonBox = QDialogButtonBox(QDialogButtonBox.Ok)
        dialog.buttonBox.accepted.connect(dialog.accept)

        dialog.layout = QVBoxLayout()
        halpin = QComboBox()
        halpin.addItem("")
        for jnum in range(9):
            halpin.addItem(f"joint.{jnum}.home-sw-in")
        halpin.addItem("motion.probe-input")
        halpin.addItem("iocontrol.0.emc-enable-in")

        net = self.plugin_setup.get("signals", {}).get("bit", {}).get("net", "")
        if net:
            index = halpin.findText(net, Qt.MatchFixedString)
            if index == -1:
                halpin.addItem(net)
                index = halpin.findText(net, Qt.MatchFixedString)
            halpin.setCurrentIndex(index)

        dialog.layout.addWidget(halpin)
        dialog.layout.addWidget(dialog.buttonBox)
        dialog.setLayout(dialog.layout)

        if dialog.exec():
            halpin = halpin.currentText()
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
