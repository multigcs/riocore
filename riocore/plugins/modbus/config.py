import os
import json
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import (
    QComboBox,
    QDialog,
    QCheckBox,
    QDialogButtonBox,
    QDoubleSpinBox,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPlainTextEdit,
    QPushButton,
    QSpinBox,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
)


DEVICE_TEMPLATES = {
    "NT18B07": {
        "image": "NT18B07.jpg",
        "info": "7x Temperature Input (NTC)",
        "comment": "",
        "setup": {
            "temp7": {"address": 18, "type": 3, "register": 0, "values": 2, "scale": 0.1, "unit": "\u00b0C", "error_values": "", "format": "0.1f", "timeout": 100, "delay": 60, "direction": "input"},
        },
    },
    "DDS519MR": {
        "image": "DDS519MR.jpg",
        "info": "Energie-Meter",
        "comment": "needs to change serial setup (Parity: even -> none)",
        "setup": {
            "voltage": {
                "address": 16,
                "type": 4,
                "register": 0,
                "is_float": True,
                "values": 1,
                "scale": 1.0,
                "unit": "V",
                "error_values": "",
                "format": "0.1f",
                "timeout": 100,
                "delay": 60,
                "direction": "input",
            },
            "current": {
                "address": 16,
                "type": 4,
                "register": 8,
                "is_float": True,
                "values": 1,
                "scale": 1.0,
                "unit": "A",
                "error_values": "",
                "format": "0.2f",
                "timeout": 100,
                "delay": 60,
                "direction": "input",
            },
            "power": {
                "address": 16,
                "type": 4,
                "register": 18,
                "is_float": True,
                "values": 1,
                "scale": 1.0,
                "unit": "W",
                "error_values": "",
                "format": "0.1f",
                "timeout": 100,
                "delay": 60,
                "direction": "input",
            },
            "power_factor": {
                "address": 16,
                "type": 4,
                "register": 42,
                "is_float": True,
                "values": 1,
                "scale": 1.0,
                "unit": "Cos",
                "error_values": "",
                "format": "0.2f",
                "timeout": 100,
                "delay": 60,
                "direction": "input",
            },
            "freq": {
                "address": 16,
                "type": 4,
                "register": 54,
                "is_float": True,
                "values": 1,
                "scale": 1.0,
                "unit": "Hz",
                "error_values": "",
                "format": "0.1f",
                "timeout": 100,
                "delay": 60,
                "direction": "input",
            },
            "power_total": {
                "address": 16,
                "type": 4,
                "register": 256,
                "is_float": True,
                "values": 1,
                "scale": 1.0,
                "unit": "kWh",
                "error_values": "",
                "format": "0.1f",
                "timeout": 100,
                "delay": 60,
                "direction": "input",
            },
        },
    },
    "EBYTE MA01-AXCX4020": {
        "image": "MA01-AXCX4020.jpg",
        "info": "4x Digital In / 2x Digital Out (Relais)",
        "comment": "",
        "setup": {
            "do2": {"address": 11, "type": 15, "register": 0, "values": 2, "scale": 1.0, "unit": "", "error_values": "0 0", "format": "d", "timeout": 100, "delay": 60, "direction": "output"},
            "di4": {"address": 11, "type": 2, "register": 0, "values": 4, "scale": 1.0, "unit": "", "error_values": "", "format": "d", "timeout": 100, "delay": 60, "direction": "input"},
        },
    },
    "EBYTE MA01-XACX0440": {
        "image": "MA01-XACX0440.jpg",
        "info": "4x Analog-In (0-20mA) / 4x Digital-Out (Relais)",
        "comment": "",
        "setup": {
            "do4": {"address": 32, "type": 15, "register": 0, "values": 4, "scale": 1.0, "unit": "", "error_values": "", "format": "d", "timeout": 100, "delay": 60, "direction": "output"},
            "ain": {"address": 32, "type": 4, "register": 0, "values": 4, "delay": 100, "scale": 0.0061, "unit": "mA", "format": "04.1f", "direction": "input"},
        },
    },
}


class config:
    fc_mapping = {
        1: ("Read Coil Status", "input"),
        2: ("Read Input Status", "input"),
        3: ("Read Holding Registers", "input"),
        4: ("Read Input Registers ", "input"),
        5: ("Force Single Coil", "output"),
        6: ("Force Single Register", "output"),
        15: ("Force Multiple Coils", "output"),
        16: ("Preset Multiple Registers", "output"),
        101: ("Huanyang VFD", "output"),
    }

    def __init__(self, instance, styleSheet=None):
        self.styleSheet = styleSheet
        self.instance = instance
        self.config = self.instance.plugin_setup.get("config", {})
        self.config_selected = None
        self.widgets = {
            "name": {
                "type": str,
                "description": "Value-Name",
                "default": "",
            },
            "address": {
                "description": "Slave-Address",
                "type": int,
                "min": 1,
                "max": 253,
                "default": 1,
            },
            "type": {
                "description": "Function-Code",
                "type": "combo",
                "options": [],
                "default": "",
            },
            "register": {
                "description": "start register",
                "type": int,
                "min": 0,
                "max": 65534,
                "default": 0,
                "on_special": False,
            },
            "values": {
                "description": "number of values",
                "type": int,
                "min": 1,
                "max": 16,
                "default": 1,
                "on_special": False,
            },
            "is_float": {
                "description": "data format is float (4byte)",
                "type": bool,
                "default": False,
                "on_special": False,
            },
            "scale": {
                "description": "Value-Scale",
                "type": float,
                "decimals": 6,
                "default": 1.0,
                "on_special": False,
            },
            "unit": {
                "description": "Unit-String",
                "type": str,
                "default": "",
                "on_special": False,
            },
            "error_values": {
                "description": "default values on connection error",
                "type": str,
                "default": "",
                "on_special": False,
            },
            "format": {
                "description": "Display-Format",
                "type": str,
                "default": "d",
                "on_special": False,
            },
            "timeout": {
                "description": "response timeout",
                "type": int,
                "min": 100,
                "max": 100000,
                "default": 100,
            },
            "delay": {
                "description": "Delay after receive (free bus)",
                "type": int,
                "min": 0,
                "max": 1000,
                "default": 60,
            },
        }

        for fc_id, fc_data in self.fc_mapping.items():
            self.widgets["type"]["options"].append(f"{fc_id} {fc_data[0]}")

    def add_item(self, item):
        self.config_selected = None
        for name, data in self.widgets.items():
            if name == "name":
                value = ""
            else:
                value = data["default"]
            if data["type"] == "combo":
                for n in range(0, data["widget"].count()):
                    if data["widget"].itemText(n).startswith(f"{value} "):
                        data["widget"].setCurrentIndex(n)
            elif data["type"] is bool:
                data["widget"].setChecked(value)
            elif data["type"] is int:
                data["widget"].setValue(value)
            elif data["type"] is float:
                data["widget"].setValue(value)
            else:
                data["widget"].setText(str(value))

    def del_item(self, item):
        config_name = self.widgets["name"]["widget"].text()
        if config_name in self.config:
            del self.config[config_name]
        self.table_load()

    def save_item(self, item):
        config_name = self.widgets["name"]["widget"].text()
        if not config_name:
            return

        if config_name not in self.config:
            self.config[config_name] = {}

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
            if name != "name":
                self.config[config_name][name] = value

        self.config[config_name]["direction"] = self.fc_mapping[self.config[config_name]["type"]][1]
        self.table_load()

    def table_load(self):
        self.tableWidget.setRowCount(len(self.config))
        row_n = 0
        for name, entry in self.config.items():
            address = str(entry.get("address", ""))
            ctype = entry.get("type", "")
            values = entry.get("values", "")
            type_text = f"{ctype} {self.fc_mapping.get(ctype, ctype)[0]}"
            self.tableWidget.setItem(row_n, 0, QTableWidgetItem(name))
            self.tableWidget.setItem(row_n, 1, QTableWidgetItem(address))
            self.tableWidget.setItem(row_n, 2, QTableWidgetItem(str(values)))
            self.tableWidget.setItem(row_n, 3, QTableWidgetItem(type_text))
            row_n += 1
        self.tableWidget.setColumnWidth(0, 100)
        self.tableWidget.setColumnWidth(1, 50)
        self.tableWidget.setColumnWidth(2, 50)
        self.tableWidget.resizeColumnToContents(3)

    def table_select(self, item):
        config_name = self.tableWidget.item(item, 0).text()
        self.config_selected = config_name
        for name, data in self.widgets.items():
            if name == "name":
                value = config_name
            else:
                value = self.config[config_name].get(name, data["default"])
            if data["type"] == "combo":
                for n in range(0, data["widget"].count()):
                    if data["widget"].itemText(n).startswith(f"{value} "):
                        data["widget"].setCurrentIndex(n)
            elif data["type"] is bool:
                data["widget"].setChecked(value)
            elif data["type"] is int:
                data["widget"].setValue(value)
            elif data["type"] is float:
                data["widget"].setValue(value)
            else:
                data["widget"].setText(str(value))

        is_special = self.config[config_name].get("type", self.widgets["type"]["default"]) > 100
        for name, data in self.widgets.items():
            if is_special and not data.get("on_special", True):
                data["widget"].setEnabled(False)
            else:
                data["widget"].setEnabled(True)

    def on_type_change(self, item):
        ctype = self.widgets["type"]["widget"].currentText().split()[0]
        is_special = int(ctype) > 100
        for name, data in self.widgets.items():
            if is_special and not data.get("on_special", True):
                data["widget"].setEnabled(False)
            else:
                data["widget"].setEnabled(True)

    def select_template(self):
        def change(row, column):
            selected = table.item(row, 0).text()
            device_data = DEVICE_TEMPLATES[selected]
            image_name = device_data.get("image")
            if image_name:
                image_file = f"{os.path.dirname(__file__)}/images/{image_name}"
                pixmap = QPixmap(image_file)
                image.setPixmap(pixmap.scaled(200, 200, Qt.KeepAspectRatio))
            template_name.setText(selected)
            info.setText(device_data["info"])
            description_text = f"{device_data['comment']}\n\n{json.dumps(device_data['setup'], indent=4)}"
            description.clear()
            description.insertPlainText(description_text)

        infotext = ""
        descriptiontext = ""

        dialog = QDialog()
        dialog.setWindowTitle("select Template")
        dialog.setFixedWidth(800)
        dialog.setFixedHeight(600)
        if self.styleSheet:
            dialog.setStyleSheet(self.styleSheet)

        dialog.buttonBox = QDialogButtonBox(QDialogButtonBox.Ok)
        dialog.buttonBox.accepted.connect(dialog.accept)
        dialog.layout = QVBoxLayout()
        hlayout = QHBoxLayout()
        vlayout_left = QVBoxLayout()

        message = QLabel("Template-Name:")
        vlayout_left.addWidget(message)

        table = QTableWidget()
        table.setColumnCount(1)
        table.setHorizontalHeaderItem(0, QTableWidgetItem("Templates"))

        table.setRowCount(len(DEVICE_TEMPLATES))

        for row, device in enumerate(DEVICE_TEMPLATES):
            pitem = QTableWidgetItem(device)
            table.setItem(row, 0, pitem)

        table.setFixedWidth(200)
        vlayout_left.addWidget(table)

        image = QLabel()
        image.setFixedWidth(200)
        image.setFixedHeight(200)

        vlayout_left.addWidget(image)

        vlayout = QVBoxLayout()
        template_name = QLabel("")
        vlayout.addWidget(template_name)

        info = QLabel(infotext)
        vlayout.addWidget(info)

        description = QPlainTextEdit()
        description.clear()
        description.insertPlainText(descriptiontext)

        vlayout.addWidget(description)
        hlayout.addLayout(vlayout_left)
        hlayout.addLayout(vlayout)
        dialog.layout.addLayout(hlayout)
        table.cellClicked.connect(change)

        dialog.layout.addWidget(dialog.buttonBox)
        dialog.setLayout(dialog.layout)

        if dialog.exec():
            template = template_name.text()
            if template in DEVICE_TEMPLATES:
                device_data = DEVICE_TEMPLATES[template]
                for key, value in device_data["setup"].items():
                    self.config[key] = value
                self.table_load()
            return ""

    def run(self):
        dialog = QDialog()
        if self.styleSheet:
            dialog.setStyleSheet(self.styleSheet)
        dialog.setWindowTitle("Modbus-Configuration")
        dialog.setMinimumWidth(800)
        dialog.setMinimumHeight(600)
        dialog.buttonBox = QDialogButtonBox(QDialogButtonBox.Ok)
        dialog.buttonBox.accepted.connect(dialog.accept)

        dialog.layout = QVBoxLayout()
        hlayout = QHBoxLayout()
        vlayout_left = QVBoxLayout()

        message = QLabel("Modbus-Values:")
        vlayout_left.addWidget(message)

        self.tableWidget = QTableWidget()
        self.tableWidget.setColumnCount(4)
        self.tableWidget.setHorizontalHeaderLabels(["Name", "Addr", "Val's", "Type"])
        self.tableWidget.cellClicked.connect(self.table_select)
        self.table_load()

        vlayout_left.addWidget(self.tableWidget)
        edit_layout = QGridLayout()

        row_n = 0
        for name, data in self.widgets.items():
            if data["type"] == "combo":
                data["widget"] = QComboBox()
                for option in data["options"]:
                    data["widget"].addItem(option)
                if name == "type":
                    data["widget"].activated.connect(self.on_type_change)
            elif data["type"] is bool:
                data["widget"] = QCheckBox()
                data["widget"].setChecked(data["default"])
            elif data["type"] is int:
                data["widget"] = QSpinBox()
                data["widget"].setValue(data["default"])
                data["widget"].setMinimum(data["min"])
                data["widget"].setMaximum(data["max"])
            elif data["type"] is float:
                data["widget"] = QDoubleSpinBox()
                data["widget"].setValue(data["default"])
                data["widget"].setDecimals(data["decimals"])
            else:
                data["widget"] = QLineEdit(data["default"])
            data["widget"].setToolTip(data["description"])

            edit_layout.addWidget(QLabel(f"{name.replace('_', ' ').title()}:"), row_n, 1)
            edit_layout.addWidget(data["widget"], row_n, 2)
            row_n += 1

        button_add = QPushButton("New")
        button_add.clicked.connect(self.add_item)
        edit_layout.addWidget(button_add, row_n, 1)

        button_save = QPushButton("Save")
        button_save.clicked.connect(self.save_item)
        edit_layout.addWidget(button_save, row_n, 2)

        button_del = QPushButton("Remove")
        button_del.clicked.connect(self.del_item)
        edit_layout.addWidget(button_del, row_n + 1, 1)

        button_template = QPushButton("Template")
        button_template.clicked.connect(self.select_template)
        edit_layout.addWidget(button_template, row_n + 1, 2)

        hlayout.addLayout(vlayout_left)
        hlayout.addLayout(edit_layout)

        dialog.layout.addLayout(hlayout)

        dialog.layout.addWidget(dialog.buttonBox)
        dialog.setLayout(dialog.layout)

        if len(self.config):
            self.table_select(0)

        if dialog.exec():
            self.instance.plugin_setup["config"] = self.config
            return ""
