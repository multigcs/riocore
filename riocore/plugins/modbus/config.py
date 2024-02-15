from PyQt5 import QtGui, QtSvg
from PyQt5.QtCore import QDateTime, QSize, Qt, QTimer
from PyQt5.QtGui import QColor, QFont, QStandardItem, QStandardItemModel
from PyQt5.QtWidgets import (
    QAbstractItemView,
    QApplication,
    QCheckBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QDoubleSpinBox,
    QFileDialog,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QMessageBox,
    QPlainTextEdit,
    QPushButton,
    QScrollArea,
    QSlider,
    QSpinBox,
    QTableWidget,
    QTableWidgetItem,
    QTabWidget,
    QTreeView,
    QVBoxLayout,
    QWidget,
)


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
    }

    def __init__(self, instance):
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
                "min": 1,
                "max": 65535,
                "default": 0,
            },
            "values": {
                "description": "number of values",
                "type": int,
                "min": 1,
                "max": 16,
                "default": 1,
            },
            "delay": {
                "description": "Delay after receive (free bus)",
                "type": int,
                "min": 0,
                "max": 1000,
                "default": 0,
            },
            "scale": {
                "description": "Value-Scale",
                "type": float,
                "default": 1.0,
            },
            "unit": {
                "description": "Unit-String",
                "type": str,
                "default": "",
            },
            "format": {
                "description": "Display-Format",
                "type": str,
                "default": "d",
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
            elif data["type"] == int:
                data["widget"].setValue(value)
            elif data["type"] == float:
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
            elif data["type"] == int:
                value = data["widget"].value()
            elif data["type"] == float:
                value = data["widget"].value()
            else:
                value = data["widget"].text()
            if name != "name":
                self.config[config_name][name] = value

        self.config[config_name]["direction"] = self.fc_mapping[
            self.config[config_name]["type"]
        ][1]

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
                value = self.config[config_name].get(name)
            if data["type"] == "combo":
                for n in range(0, data["widget"].count()):
                    if data["widget"].itemText(n).startswith(f"{value} "):
                        data["widget"].setCurrentIndex(n)
            elif data["type"] == int:
                data["widget"].setValue(value)
            elif data["type"] == float:
                data["widget"].setValue(value)
            else:
                data["widget"].setText(str(value))

    def run(self):
        dialog = QDialog()
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
            elif data["type"] == int:
                data["widget"] = QSpinBox()
                data["widget"].setValue(data["default"])
                data["widget"].setMinimum(data["min"])
                data["widget"].setMaximum(data["max"])
            elif data["type"] == float:
                data["widget"] = QDoubleSpinBox()
                data["widget"].setValue(data["default"])
            else:
                data["widget"] = QLineEdit(data["default"])
            data["widget"].setToolTip(data["description"])

            edit_layout.addWidget(QLabel(f"{name.title()}:"), row_n, 1)
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
