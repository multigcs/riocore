import glob
import importlib
import os
import sys
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
    QWidget,
)

from riocore.widgets import STYLESHEET_CHECKBOX

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

        sys.path.insert(0, plugin_path)
        self.device_types = {}
        for device_path in sorted(glob.glob(os.path.join(plugin_path, "devices", "*.py"))):
            device_name = os.path.basename(device_path).replace(".py", "")
            if not device_name.startswith("_"):
                devlib = importlib.import_module(f".{device_name}", ".devices")
                self.device_types[device_name] = devlib.i2c_device.options

        self.widgets = {
            "name": {
                "type": str,
                "description": "Value-Name",
                "default": "",
            },
            "address": {
                "description": "Slave-Address",
                "type": "combo",
                "options": [],
                "default": "",
            },
            "type": {
                "description": "Device-Type",
                "type": "combo",
                "options": self.device_types,
                "default": "",
            },
        }

    def read_widget(self, data):
        value = ""
        if data["type"] == "combo":
            value = data["widget"].currentText().split()[0]
            if value.isnumeric():
                value = int(value)
        elif data["type"] == "bits":
            value = 0
            for bit_n, widget in enumerate(data.get("bits", [])):
                if widget.isChecked():
                    value |= 1 << (7 - bit_n)
        elif data["type"] is bool:
            value = data["widget"].isChecked()
        elif data["type"] is int:
            value = data["widget"].value()
        elif data["type"] is float:
            value = data["widget"].value()
        else:
            value = data["widget"].text()
        return value

    def add_widget(self, data, value):
        if data["type"] == "combo":
            data["widget"] = QComboBox()
            for option in data["options"]:
                data["widget"].addItem(option)
            for n in range(0, data["widget"].count()):
                if data["widget"].itemText(n) == value:
                    data["widget"].setCurrentIndex(n)

        elif data["type"] == "bits":
            blayout = QHBoxLayout()
            data["widget"] = QWidget()
            data["widget"].setLayout(blayout)
            data["bits"] = []
            for bit in reversed(range(8)):
                vlayout = QVBoxLayout()
                vwidget = QWidget()
                vwidget.setLayout(vlayout)
                bcheck = QCheckBox()
                bcheck.setStyleSheet(STYLESHEET_CHECKBOX)
                bcheck.setChecked((value & (1 << bit)))
                data["bits"].append(bcheck)
                vlayout.addWidget(QLabel(f"{bit}"), stretch=0)
                vlayout.addWidget(bcheck, stretch=0)
                blayout.addWidget(vwidget, stretch=0)
            blayout.addStretch()

        elif data["type"] is bool:
            data["widget"] = QCheckBox()
            data["widget"].setStyleSheet(STYLESHEET_CHECKBOX)
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
        return data["widget"]

    def edit_item(self, config_name):
        if config_name not in self.config["devices"]:
            prefix = "device"
            dnum = 0
            while f"{prefix}{dnum}" in self.config["devices"]:
                dnum += 1
            config_name = f"{prefix}{dnum}"

        dtype = self.config["devices"].get(config_name, {}).get("type", "")

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

        vlayout.addWidget(QLabel("Device-Setup:"), stretch=0)

        def update_mask(item):
            dtype = self.widgets["type"]["widget"].currentText()

            if dtype in self.device_types:
                self.widgets["address"]["options"] = self.device_types[dtype]["addresses"]
            else:
                self.widgets["address"]["options"] = []

            self.widgets["address"]["widget"].clear()
            for option in self.widgets["address"]["options"]:
                self.widgets["address"]["widget"].addItem(option)

            value = self.config["devices"].get(config_name, {}).get("address", data["default"])
            for n in range(0, self.widgets["address"]["widget"].count()):
                if self.widgets["address"]["widget"].itemText(n) == value:
                    self.widgets["address"]["widget"].setCurrentIndex(n)

            # clean extra config widgets
            for i in reversed(range(self.device_layout.count())):
                widget = self.device_layout.itemAt(i).widget()
                self.device_layout.removeWidget(widget)
                widget.deleteLater()

            if dtype in self.device_types and "config" in self.device_types[dtype]:
                self.device_layout.addWidget(QLabel("Device-Options:"), stretch=0)
                for name, cdata in self.device_types[dtype]["config"].items():
                    value = value = self.config["devices"].get(config_name, {}).get(name, cdata["default"])
                    self.device_layout.addWidget(QLabel(f"{name.replace('_', ' ').title()}:"))
                    widget = self.add_widget(cdata, value)
                    self.device_layout.addWidget(widget)

        if dtype in self.device_types:
            self.widgets["address"]["options"] = self.device_types[dtype]["addresses"]
        else:
            self.widgets["address"]["options"] = []

        for name, data in self.widgets.items():
            if name == "name":
                value = config_name
            else:
                value = self.config["devices"].get(config_name, {}).get(name, data["default"])
            self.add_widget(data, value)

            hlayout = QHBoxLayout()
            hlayout.addWidget(QLabel(f"{name.replace('_', ' ').title()}:"))
            hlayout.addWidget(data["widget"])
            vlayout.addLayout(hlayout, stretch=0)

        self.widgets["type"]["widget"].currentIndexChanged.connect(update_mask)

        self.device_layout = QVBoxLayout()
        dialog.layout.addLayout(vlayout)
        dialog.layout.addLayout(self.device_layout)
        dialog.layout.addStretch()
        dialog.layout.addWidget(dialog.buttonBox, stretch=0)
        dialog.setLayout(dialog.layout)

        update_mask(None)

        if dialog.exec():
            new_config = {}
            for name, data in self.widgets.items():
                value = self.read_widget(data)
                if name == "name":
                    new_name = value
                else:
                    new_config[name] = value

            if dtype in self.device_types and "config" in self.device_types[dtype]:
                for name, cdata in self.device_types[dtype]["config"].items():
                    value = self.read_widget(cdata)
                    new_config[name] = value

            if new_name != config_name and config_name in self.config["devices"]:
                del self.config["devices"][config_name]

            self.config["devices"][new_name] = new_config
            self.instance.plugin_setup["config"]["devices"] = self.config["devices"]
            self.table_load()

    def del_item(self, item):
        config_name = self.config_selected
        if config_name in self.config["devices"]:
            del self.config["devices"][config_name]
        self.table_load()

    def table_load(self):
        self.tableWidget.setRowCount(len(self.config["devices"]))
        row_n = 0
        for name, entry in self.config["devices"].items():
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
            self.instance.plugin_setup["config"] = self.config
            return ""
