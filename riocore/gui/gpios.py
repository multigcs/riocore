from riocore import gpios

from PyQt5.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QVBoxLayout,
)


class GuiGpios:
    def __init__(self, parent):
        self.parent = parent

    def edit_gpio(self, widget=None, pin_select=None):
        dialog = QDialog()
        dialog.setWindowTitle(f"edit gpio mode ({pin_select})")

        dialog.layout = QVBoxLayout()
        dialog_buttonBox = QDialogButtonBox(QDialogButtonBox.Cancel | QDialogButtonBox.Ok)
        dialog_buttonBox.accepted.connect(dialog.accept)
        dialog_buttonBox.rejected.connect(dialog.reject)
        dialog.setLayout(dialog.layout)

        combo = QComboBox()
        combo.addItem("Input")
        combo.addItem("Output")
        combo.addItem("Output+Reset")
        dialog.layout.addWidget(combo)
        dialog.layout.addWidget(dialog_buttonBox)

        if dialog.exec():
            gpio_config = self.parent.config.get("gpios", [])
            for gpio in gpio_config:
                if "pins" not in gpio:
                    gpio["pins"] = {}
                gtype = gpio.get("type")
                if gtype == "rpi":
                    for pmode in ("inputs", "outputs", "reset"):
                        if pmode not in gpio["pins"]:
                            gpio["pins"][pmode] = []
                        if pin_select in gpio["pins"][pmode]:
                            gpio["pins"][pmode].remove(pin_select)
                    if combo.currentText() == "Input":
                        gpio["pins"]["inputs"].append(pin_select)
                    elif combo.currentText() == "Output":
                        gpio["pins"]["inputs"].append(pin_select)
                    elif combo.currentText() == "Output+Reset":
                        gpio["pins"]["outputs"].append(pin_select)
                        gpio["pins"]["reset"].append(pin_select)

            if not self.parent.args.nographs:
                self.parent.tabs["Overview"].update()
            self.parent.tabs["GPIOs"].update()
            self.parent.tabs["Json"].update()

    def add_gpio_parport(self):
        dialog = QDialog()
        dialog.setWindowTitle("add parport")
        dialog.layout = QVBoxLayout()
        dialog_buttonBox = QDialogButtonBox(QDialogButtonBox.Cancel | QDialogButtonBox.Ok)
        dialog_buttonBox.accepted.connect(dialog.accept)
        dialog_buttonBox.rejected.connect(dialog.reject)
        dialog.setLayout(dialog.layout)

        combo_mode = QComboBox()
        for pmode in ("in", "out", "epp", "x"):
            combo_mode.addItem(pmode)
        dialog.layout.addWidget(combo_mode)

        combo = QComboBox()
        for addr in ("0x378", "0x278"):
            combo.addItem(addr)
        dialog.layout.addWidget(combo)
        dialog.layout.addWidget(dialog_buttonBox)

        if dialog.exec():
            address = combo.currentText()
            pmode = combo_mode.currentText()
            if "gpios" not in self.parent.config:
                self.parent.config["gpios"] = []
            self.parent.config["gpios"].append(
                {
                    "type": "parport",
                    "address": address,
                    "mode": pmode,
                }
            )
            self.parent.tabs["GPIOs"].update()

    def add_gpio(self, widget=None):
        dialog = QDialog()
        dialog.setWindowTitle("select component or set net")

        dialog.layout = QVBoxLayout()
        dialog_buttonBox = QDialogButtonBox(QDialogButtonBox.Cancel | QDialogButtonBox.Ok)
        dialog_buttonBox.accepted.connect(dialog.accept)
        dialog_buttonBox.rejected.connect(dialog.reject)
        dialog.setLayout(dialog.layout)

        combo = QComboBox()
        for gclass in dir(gpios):
            if gclass.startswith("gpio_"):
                gtype = gclass.replace("gpio_", "")
                combo.addItem(gtype)
        dialog.layout.addWidget(combo)
        dialog.layout.addWidget(dialog_buttonBox)

        if dialog.exec():
            if combo.currentText() == "parport":
                self.add_gpio_parport()
            else:
                if "gpios" not in self.parent.config:
                    self.parent.config["gpios"] = []
                self.parent.config["gpios"].append(
                    {
                        "type": "rpi",
                    }
                )
                self.parent.tabs["GPIOs"].update()
