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
    QWidget,
    QTabWidget,
)


DEVICE_TEMPLATES = {
    "NT18B07": {
        "image": "NT18B07.jpg",
        "info": "7x Temperature Input (NTC)",
        "comment": "7channel Temperature sensors",
        "setup": {
            "temp7": {
                "address": 18,
                "type": 3,
                "register": 0,
                "values": 2,
                "scale": 0.1,
                "unit": "\u00b0C",
                "error_values": "",
                "format": "0.1f",
                "datatype": "int",
                "timeout": 100,
                "delay": 60,
                "direction": "input",
            },
        },
    },
    "N4D3E16": {
        "image": "N4D3E16.png",
        "info": "16channel IO",
        "comment": "16channel input + 16channel output TODO: add inputs",
        "setup": {
            "relais1_16": {
                "address": 1,
                "type": 6,
                "register": 112,
                "datatype": "bool",
                "values": 16,
                "scale": 1.0,
                "unit": "V",
                "error_values": "",
                "format": "0.1f",
                "timeout": 100,
                "delay": 60,
                "direction": "output",
                "priority": 5,
            },
        },
    },
    "N4DOK32": {
        "image": "N4DOK32.png",
        "info": "32channel relais output",
        "comment": "32channel relais output",
        "setup": {
            "relais1_16": {
                "address": 1,
                "type": 6,
                "register": 112,
                "datatype": "bool",
                "values": 16,
                "scale": 1.0,
                "unit": "V",
                "error_values": "",
                "format": "0.1f",
                "timeout": 100,
                "delay": 60,
                "direction": "output",
                "priority": 5,
            },
            "relais17_32": {
                "address": 1,
                "type": 6,
                "register": 113,
                "datatype": "bool",
                "values": 16,
                "scale": 1.0,
                "unit": "V",
                "error_values": "",
                "format": "0.1f",
                "timeout": 100,
                "delay": 60,
                "direction": "output",
                "priority": 5,
            },
        },
    },
    "DDS519MR": {
        "image": "DDS519MR.jpg",
        "info": "Energie-Meter",
        "comment": "you have to change serial setup (Parity: even -> none)",
        "setup": {
            "voltage": {
                "address": 16,
                "type": 4,
                "register": 0,
                "datatype": "float",
                "values": 1,
                "scale": 1.0,
                "unit": "V",
                "error_values": "",
                "format": "0.1f",
                "timeout": 300,
                "delay": 150,
                "direction": "input",
            },
            "current": {
                "address": 16,
                "type": 4,
                "register": 8,
                "datatype": "float",
                "values": 1,
                "scale": 1.0,
                "unit": "A",
                "error_values": "",
                "format": "0.2f",
                "timeout": 300,
                "delay": 150,
                "direction": "input",
            },
            "power": {
                "address": 16,
                "type": 4,
                "register": 18,
                "datatype": "float",
                "values": 1,
                "scale": 1.0,
                "unit": "W",
                "error_values": "",
                "format": "0.1f",
                "timeout": 300,
                "delay": 150,
                "direction": "input",
            },
            "power_factor": {
                "address": 16,
                "type": 4,
                "register": 42,
                "datatype": "float",
                "values": 1,
                "scale": 1.0,
                "unit": "Cos",
                "error_values": "",
                "format": "0.2f",
                "timeout": 300,
                "delay": 150,
                "direction": "input",
            },
            "freq": {
                "address": 16,
                "type": 4,
                "register": 54,
                "datatype": "float",
                "values": 1,
                "scale": 1.0,
                "unit": "Hz",
                "error_values": "",
                "format": "0.1f",
                "timeout": 300,
                "delay": 150,
                "direction": "input",
            },
            "power_total": {
                "address": 16,
                "type": 4,
                "register": 256,
                "datatype": "float",
                "values": 1,
                "scale": 1.0,
                "unit": "kWh",
                "error_values": "",
                "format": "0.1f",
                "timeout": 300,
                "delay": 150,
                "direction": "input",
            },
        },
    },
    "EBYTE MA01-AXCX4020": {
        "image": "MA01-AXCX4020.jpg",
        "info": "4 x Digital In + 2 x Digital Out",
        "comment": "4x Digital In / 2x Digital Out (Relais)",
        "setup": {
            "do2": {
                "address": 11,
                "type": 15,
                "register": 0,
                "values": 2,
                "scale": 1.0,
                "unit": "",
                "error_values": "0 0",
                "format": "d",
                "timeout": 100,
                "delay": 60,
                "direction": "output",
                "datatype": "bool",
                "priority": 5,
            },
            "di4": {
                "address": 11,
                "type": 2,
                "register": 0,
                "values": 4,
                "scale": 1.0,
                "unit": "",
                "error_values": "",
                "format": "d",
                "timeout": 100,
                "delay": 60,
                "datatype": "bool",
                "direction": "input",
            },
        },
    },
    "EBYTE MA01-XACX0440": {
        "image": "MA01-XACX0440.jpg",
        "info": "4 x Analog In + 4 x Digital Out",
        "comment": "4x Analog-In (0-20mA) / 4x Digital-Out (Relais)",
        "setup": {
            "do4": {
                "address": 32,
                "type": 15,
                "register": 0,
                "values": 4,
                "scale": 1.0,
                "unit": "",
                "error_values": "",
                "format": "d",
                "timeout": 100,
                "delay": 60,
                "datatype": "bool",
                "direction": "output",
                "priority": 5,
            },
            "ain": {
                "address": 32,
                "type": 4,
                "register": 0,
                "values": 4,
                "delay": 100,
                "scale": 0.0061,
                "unit": "mA",
                "format": "04.1f",
                "datatype": "bool",
                "direction": "input",
            },
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
        201: ("Custom Boolean", "output"),
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
                "tab": "general",
            },
            "address": {
                "description": "Slave-Address",
                "type": int,
                "min": 1,
                "max": 253,
                "default": 1,
                "tab": "general",
            },
            "type": {
                "description": "Function-Code",
                "type": "combo",
                "options": [],
                "default": "",
                "tab": "general",
            },
            "register": {
                "description": "start register",
                "type": int,
                "min": 0,
                "max": 65534,
                "default": 0,
                "on_special": False,
                "tab": "general",
            },
            "values": {
                "description": "number of values",
                "type": int,
                "min": 1,
                "max": 16,
                "default": 1,
                "on_special": False,
                "tab": "general",
            },
            "datatype": {
                "description": "data format",
                "type": "combo",
                "options": ["float", "int", "bool"],
                "default": "float",
                "on_special": False,
                "tab": "general",
            },
            "scale": {
                "description": "Value-Scale",
                "type": float,
                "decimals": 6,
                "default": 1.0,
                "on_special": False,
                "tab": "misc",
            },
            "unit": {
                "description": "Unit-String",
                "type": str,
                "default": "",
                "on_special": False,
                "tab": "misc",
            },
            "error_values": {
                "description": "default values on connection error",
                "type": str,
                "default": "",
                "on_special": False,
                "tab": "misc",
            },
            "format": {
                "description": "Display-Format",
                "type": str,
                "default": "d",
                "on_special": False,
                "tab": "misc",
            },
            "timeout": {
                "description": "response timeout",
                "type": int,
                "min": 100,
                "max": 100000,
                "default": 100,
                "tab": "misc",
            },
            "delay": {
                "description": "Delay after receive (free bus)",
                "type": int,
                "min": 0,
                "max": 1000,
                "default": 60,
                "tab": "misc",
            },
            "priority": {
                "description": "output priority / change detection",
                "type": int,
                "min": 0,
                "max": 9,
                "default": 0,
                "tab": "misc",
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
                    if data["widget"].itemText(n) == value or data["widget"].itemText(n).startswith(f"{value} "):
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
        table_item = self.tableWidget.item(item, 0)
        if not table_item:
            return
        config_name = table_item.text()
        self.config_selected = config_name
        for name, data in self.widgets.items():
            if name == "name":
                value = config_name
            else:
                value = self.config[config_name].get(name, data["default"])
            if data["type"] == "combo":
                for n in range(0, data["widget"].count()):
                    if data["widget"].itemText(n) == value or data["widget"].itemText(n).startswith(f"{value} "):
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
                image_file = os.path.join(os.path.dirname(__file__), "images", image_name)
                pixmap = QPixmap(image_file)
                image.setPixmap(pixmap.scaled(200, 200, Qt.KeepAspectRatio))
            template_name.setText(selected)
            info.setText(device_data["info"])

            description_text = [device_data["comment"]]
            description_text.append("")
            for name, data in device_data["setup"].items():
                description_text.append(f"{name}:")
                description_text.append(f"  func: {data['type']} ({self.fc_mapping.get(data['type'], ['???'])[0]})")
                description_text.append(f"  register: {data.get('register')} values: {data.get('values')} type: {data.get('datatype')}")
                description_text.append("")

            description.clear()
            description.insertPlainText("\n".join(description_text))

        infotext = ""
        descriptiontext = ""

        dialog = QDialog()
        dialog.setWindowTitle("select Template")
        dialog.setFixedWidth(800)
        dialog.setFixedHeight(600)
        if self.styleSheet:
            dialog.setStyleSheet(self.styleSheet)

        dialog.buttonBox = QDialogButtonBox(QDialogButtonBox.Cancel | QDialogButtonBox.Ok)
        dialog.buttonBox.accepted.connect(dialog.accept)
        dialog.buttonBox.rejected.connect(dialog.reject)
        dialog.layout = QVBoxLayout()
        hlayout = QHBoxLayout()
        vlayout_left = QVBoxLayout()
        vlayout_right = QVBoxLayout()

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
        table.currentCellChanged.connect(change)

        image = QLabel()
        image.setFixedWidth(200)
        image.setFixedHeight(200)
        vlayout_right.addWidget(image, stretch=0)
        vlayout_right.addStretch()
        hlayout.addLayout(vlayout_right)

        dialog.layout.addWidget(dialog.buttonBox)
        dialog.setLayout(dialog.layout)

        change(0, 0)

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
        dialog.buttonBox = QDialogButtonBox(QDialogButtonBox.Cancel | QDialogButtonBox.Ok)
        dialog.buttonBox.accepted.connect(dialog.accept)
        dialog.buttonBox.rejected.connect(dialog.reject)

        dialog.layout = QVBoxLayout()
        hlayout = QHBoxLayout()
        dialog.layout.addLayout(hlayout)

        vlayout_left = QVBoxLayout()
        hlayout.addLayout(vlayout_left)
        vlayout_right = QVBoxLayout()
        hlayout.addLayout(vlayout_right)

        message = QLabel("Modbus-Values:")
        vlayout_left.addWidget(message)

        self.tableWidget = QTableWidget()
        self.tableWidget.setColumnCount(4)
        self.tableWidget.setHorizontalHeaderLabels(["Name", "Addr", "Val's", "Type"])
        self.tableWidget.cellClicked.connect(self.table_select)
        self.tableWidget.currentCellChanged.connect(self.table_select)
        self.table_load()
        vlayout_left.addWidget(self.tableWidget)

        tabwidget = QTabWidget()
        tab_genearal_layout = QVBoxLayout()
        tab_general_widget = QWidget()
        tab_general_widget.setLayout(tab_genearal_layout)
        tab_misc_layout = QVBoxLayout()
        tab_misc_widget = QWidget()
        tab_misc_widget.setLayout(tab_misc_layout)
        tabwidget.addTab(tab_general_widget, "General")
        tabwidget.addTab(tab_misc_widget, "Misc")
        vlayout_right.addWidget(tabwidget)

        button_layout = QGridLayout()
        vlayout_right.addLayout(button_layout)

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
            value_layout = QHBoxLayout()
            value_layout.addWidget(QLabel(f"{name.replace('_', ' ').title()}:"))
            value_layout.addWidget(data["widget"])

            if data["tab"] == "general":
                tab_genearal_layout.addLayout(value_layout)
            else:
                tab_misc_layout.addLayout(value_layout)

        button_add = QPushButton("New")
        button_add.clicked.connect(self.add_item)
        button_layout.addWidget(button_add, 0, 1)

        button_save = QPushButton("Save")
        button_save.clicked.connect(self.save_item)
        button_layout.addWidget(button_save, 0, 2)

        button_del = QPushButton("Remove")
        button_del.clicked.connect(self.del_item)
        button_layout.addWidget(button_del, 1, 1)

        button_template = QPushButton("Template")
        button_template.clicked.connect(self.select_template)
        button_layout.addWidget(button_template, 1, 2)

        dialog.layout.addWidget(dialog.buttonBox)
        dialog.setLayout(dialog.layout)

        if len(self.config):
            self.table_select(0)

        if dialog.exec():
            self.instance.plugin_setup["config"] = self.config
            return ""


if __name__ == "__main__":
    import json
    import sys
    from PyQt5.QtWidgets import QApplication

    app = QApplication(sys.argv)

    class mock_instance:
        plugin_setup = {
            "config": {
                "do4": {
                    "address": 32,
                    "type": 15,
                    "register": 0,
                    "values": 4,
                    "scale": 1.0,
                    "unit": "",
                    "error_values": "",
                    "format": "d",
                    "timeout": 100,
                    "delay": 60,
                    "datatype": "bool",
                    "direction": "output",
                    "priority": 5,
                },
                "ain": {"address": 32, "type": 4, "register": 0, "values": 4, "delay": 100, "scale": 0.0061, "unit": "mA", "format": "04.1f", "datatype": "bool", "direction": "input"},
            }
        }

    instance = mock_instance()
    config_gui = config(instance)
    config_gui.run()
    print(json.dumps(instance.plugin_setup, indent=4))
