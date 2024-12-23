import os
import glob
from PyQt5.QtWidgets import (
    QComboBox,
    QDialog,
    QCheckBox,
    QDialogButtonBox,
    QDoubleSpinBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSpinBox,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
)

plugin_path = os.path.dirname(__file__)


class config:
    def __init__(self, instance, styleSheet=None):
        self.styleSheet = styleSheet
        self.instance = instance
        if "config" not in self.instance.plugin_setup:
            self.instance.plugin_setup["config"] = {}
        if "devices" not in self.instance.plugin_setup["config"]:
            self.instance.plugin_setup["config"]["devices"] = {}
        self.config = self.instance.plugin_setup["config"]
        self.config_selected = None

        self.device_types = []
        for device_path in sorted(glob.glob(os.path.join(plugin_path, "devices", "*.py"))):
            device_name = os.path.basename(device_path).replace(".py", "")
            if not device_name.startswith("_"):
                self.device_types.append(device_name)

        self.widgets = {
            "name": {
                "type": str,
                "description": "Value-Name",
                "default": "",
            },
            "address": {
                "description": "Slave-Address",
                "type": str,
                "default": "",
            },
            "type": {
                "description": "Device-Type",
                "type": "combo",
                "options": self.device_types,
                "default": "",
            },
        }

    def edit_item(self, config_name):
        if config_name not in self.config:
            prefix = "device"
            dnum = 0
            while f"{prefix}{dnum}" in self.config:
                dnum += 1
            config_name = f"{prefix}{dnum}"

        dialog = QDialog()
        if self.styleSheet:
            dialog.setStyleSheet(self.styleSheet)
        dialog.setWindowTitle("I2C-Configuration")
        dialog.setMinimumWidth(800)
        dialog.setMinimumHeight(600)
        dialog.buttonBox = QDialogButtonBox(QDialogButtonBox.Cancel | QDialogButtonBox.Ok)
        dialog.buttonBox.accepted.connect(dialog.accept)
        dialog.buttonBox.rejected.connect(dialog.reject)

        dialog.layout = QVBoxLayout()
        vlayout = QVBoxLayout()

        message = QLabel("Device-Setup:")
        vlayout.addWidget(message, stretch=0)

        for name, data in self.widgets.items():
            if name == "name":
                value = config_name
            else:
                value = self.config.get(config_name, {}).get(name, data["default"])
            if data["type"] == "combo":
                data["widget"] = QComboBox()
                for option in data["options"]:
                    data["widget"].addItem(option)
                for n in range(0, data["widget"].count()):
                    if data["widget"].itemText(n) == value:
                        data["widget"].setCurrentIndex(n)
            elif data["type"] is bool:
                data["widget"] = QCheckBox()
                data["widget"].setChecked(value)
            elif data["type"] is int:
                data["widget"] = QSpinBox()
                data["widget"].setMinimum(data["min"])
                data["widget"].setMaximum(data["max"])
                data["widget"].setValue(value)
            elif data["type"] is float:
                data["widget"] = QDoubleSpinBox()
                data["widget"].setValue(data["default"])
                data["widget"].setDecimals(data["decimals"])
                data["widget"].setText(str(value))
            else:
                data["widget"] = QLineEdit(data["default"])
                data["widget"].setText(str(value))
            data["widget"].setToolTip(data["description"])

            hlayout = QHBoxLayout()
            hlayout.addWidget(QLabel(f"{name.replace('_', ' ').title()}:"))
            hlayout.addWidget(data["widget"])
            vlayout.addLayout(hlayout, stretch=0)

        vlayout.addStretch()
        dialog.layout.addLayout(vlayout)
        dialog.layout.addWidget(dialog.buttonBox, stretch=0)
        dialog.setLayout(dialog.layout)

        if dialog.exec():
            new_config = {}
            for name, data in self.widgets.items():
                value = ""
                if data["type"] == "combo":
                    value = data["widget"].currentText().split()[0]
                    if value.isnumeric():
                        value = int(value)
                elif data["type"] is bool:
                    value = data["widget"].isChecked()
                elif data["type"] is int:
                    value = data["widget"].value()
                elif data["type"] is float:
                    value = data["widget"].value()
                else:
                    value = data["widget"].text()
                if name == "name":
                    new_name = value
                else:
                    new_config[name] = value

            if new_name != config_name and config_name in self.config["devices"]:
                del self.config["devices"][config_name]

            self.config["devices"][new_name] = new_config
            self.instance.plugin_setup["config"]["devices"] = self.config
            self.table_load()

    def del_item(self, item):
        config_name = self.config_selected
        if config_name in self.config:
            del self.config[config_name]
        self.table_load()

    def table_load(self):
        self.tableWidget.setRowCount(len(self.config))
        row_n = 0
        for name, entry in self.config.items():
            address = str(entry.get("address", ""))
            dtype = entry.get("type", "")
            self.tableWidget.setItem(row_n, 0, QTableWidgetItem(name))
            self.tableWidget.setItem(row_n, 1, QTableWidgetItem(address))
            self.tableWidget.setItem(row_n, 2, QTableWidgetItem(dtype))
            row_n += 1

    def table_select(self, item):
        config_name = self.tableWidget.item(item, 0).text()
        self.config_selected = config_name
        self.edit_item(config_name)

    def run(self):
        dialog = QDialog()
        if self.styleSheet:
            dialog.setStyleSheet(self.styleSheet)
        dialog.setWindowTitle("I2C-Configuration")
        dialog.setMinimumWidth(800)
        dialog.setMinimumHeight(600)
        dialog.buttonBox = QDialogButtonBox(QDialogButtonBox.Cancel | QDialogButtonBox.Ok)
        dialog.buttonBox.accepted.connect(dialog.accept)
        dialog.buttonBox.rejected.connect(dialog.reject)

        dialog.layout = QVBoxLayout()
        vlayout = QVBoxLayout()

        message = QLabel("I2C-Devices:")
        vlayout.addWidget(message, stretch=0)

        self.tableWidget = QTableWidget()
        self.tableWidget.setColumnCount(3)
        self.tableWidget.setHorizontalHeaderLabels(["Name", "Addr", "Type"])
        self.tableWidget.cellClicked.connect(self.table_select)
        self.table_load()

        vlayout.addWidget(self.tableWidget, stretch=1)

        button_add = QPushButton("Add")
        button_add.clicked.connect(self.edit_item)
        vlayout.addWidget(button_add, stretch=0)

        button_del = QPushButton("Remove")
        button_del.clicked.connect(self.del_item)
        vlayout.addWidget(button_del, stretch=0)

        dialog.layout.addLayout(vlayout)

        dialog.layout.addWidget(dialog.buttonBox)
        dialog.setLayout(dialog.layout)

        if dialog.exec():
            self.instance.plugin_setup["config"]["devices"] = self.config
            return ""
