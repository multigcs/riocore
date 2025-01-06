import glob
import graphviz
import importlib
import os
import sys

from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (
    QAbstractItemView,
    QAbstractScrollArea,
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

from riocore.widgets import MyQSvgWidget, STYLESHEET_CHECKBOX

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
        for device_path in sorted(glob.glob(os.path.join(plugin_path, "devices", "*", "__init__.py"))):
            device_name = os.path.basename(os.path.dirname(device_path))
            if not device_name.startswith("_"):
                devlib = importlib.import_module(f".{device_name}", ".devices")
                self.device_types[device_name] = devlib.i2c_device.options

        self.widgets = {
            "name": {
                "type": str,
                "description": "Value-Name",
                "default": "",
            },
            "type": {
                "description": "Device-Type",
                "type": "combo",
                "options": self.device_types,
                "default": "",
            },
            "address": {
                "description": "Slave-Address",
                "type": "combo",
                "options": [],
                "default": "",
            },
            "subbus": {
                "description": "number of subbus",
                "type": "combo",
                "options": ["none", "0", "1", "2", "3", "4", "5", "6", "7"],
                "default": "",
            },
        }

    def read_widget(self, data):
        value = ""
        if data["type"] == "combo":
            value = data["widget"].currentText()
        elif data["type"] == "bits":
            value = 0
            bitwidth = data.get("width", 8)
            for bit_n, widget in enumerate(data.get("bits", [])):
                if widget.isChecked():
                    value |= 1 << ((bitwidth - 1) - bit_n)
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
            bitwidth = data.get("width", 8)
            data["widget"] = QWidget()
            data["widget"].setLayout(blayout)
            data["bits"] = []
            for bit in reversed(range(bitwidth)):
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
            data["widget"].setMinimum(data.get("min", -9999999))
            data["widget"].setMaximum(data.get("max", 9999999))
            data["widget"].setValue(value)
        elif data["type"] is float:
            data["widget"] = QDoubleSpinBox()
            data["widget"].setMinimum(data.get("min", -9999999))
            data["widget"].setMaximum(data.get("max", 9999999))
            data["widget"].setValue(data["default"])
            data["widget"].setDecimals(data.get("decimals", 3))
            data["widget"].setValue(value)
        else:
            data["widget"] = QLineEdit(data["default"])
            data["widget"].setText(str(value))
        data["widget"].setToolTip(data["description"])
        return data["widget"]

    def add_item(self, item):
        dialog = QDialog()
        dialog.setWindowTitle("select device")
        if self.styleSheet:
            dialog.setStyleSheet(self.styleSheet)

        dialog.layout = QVBoxLayout()
        dialog_buttonBox = QDialogButtonBox(QDialogButtonBox.Cancel | QDialogButtonBox.Ok)
        dialog_buttonBox.accepted.connect(dialog.accept)
        dialog_buttonBox.rejected.connect(dialog.reject)
        dialog.setLayout(dialog.layout)

        dialog.device_infos = []

        def show_device_info(idx):
            device = dialog.device_infos[idx]
            dialog.selected = device
            description = device[1].options["info"]
            description += "\n\n"
            description += device[1].options["description"]
            description_label.setText(description)

        device_table = QTableWidget()
        device_table.setColumnCount(1)
        device_table.setHorizontalHeaderItem(0, QTableWidgetItem("devices"))

        row_n = 0
        for device_path in sorted(glob.glob(os.path.join(plugin_path, "devices", "*", "__init__.py"))):
            device_name = os.path.basename(os.path.dirname(device_path))
            if not device_name.startswith("_"):
                devlib = importlib.import_module(f".{device_name}", ".devices")
                device_table.setRowCount(row_n + 1)
                pitem = QTableWidgetItem(device_name)
                device_table.setItem(row_n, 0, pitem)
                dialog.device_infos.append((device_name, devlib.i2c_device))
                row_n += 1

        header = device_table.horizontalHeader()
        header.setStretchLastSection(True)
        # device_table.setFixedWidth(200)
        device_table.cellClicked.connect(show_device_info)
        device_table.currentCellChanged.connect(show_device_info)

        left_layout = QVBoxLayout()
        left_widget = QWidget()
        left_widget.setLayout(left_layout)

        left_layout.addWidget(device_table)

        mid_layout = QVBoxLayout()
        mid_widget = QWidget()
        mid_widget.setFixedWidth(400)
        mid_widget.setLayout(mid_layout)
        name_label = QLabel("Name:")
        name_label_font = QFont()
        name_label_font.setBold(True)
        name_label.setFont(name_label_font)

        mid_layout.addWidget(name_label)
        info_label = QLabel("info")
        mid_layout.addWidget(info_label)
        description_label = QLabel("description")
        mid_layout.addWidget(description_label)
        mid_layout.addStretch()

        right_layout = QVBoxLayout()
        right_widget = QWidget()
        right_widget.setLayout(right_layout)
        image_label = QLabel("---")
        right_layout.addWidget(image_label)
        right_layout.addStretch()

        infos = QHBoxLayout()
        infos.addWidget(left_widget, stretch=0)
        infos.addWidget(mid_widget, stretch=3)
        infos.addWidget(right_widget, stretch=1)

        dialog.layout.addLayout(infos)
        dialog.layout.addWidget(dialog_buttonBox)

        if dialog.exec():
            prefix = dialog.selected[0]
            dnum = 0
            while f"{prefix}_{dnum}" in self.config["devices"]:
                dnum += 1
            config_name = f"{prefix}_{dnum}"
            self.config["devices"][config_name] = {
                "type": dialog.selected[0],
                "address": dialog.selected[1].options["addresses"][0],
            }
            self.config_selected = config_name
            self.edit_item(None)

    def edit_item(self, item):
        config_name = self.config_selected
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

            dtype = new_config["type"]
            if dtype in self.device_types and "config" in self.device_types[dtype]:
                for name, cdata in self.device_types[dtype]["config"].items():
                    value = self.read_widget(cdata)
                    new_config[name] = value

            if new_name != config_name and config_name in self.config["devices"]:
                del self.config["devices"][config_name]

            self.config["devices"][new_name] = new_config
            self.instance.plugin_setup["config"]["devices"] = self.config["devices"]
            self.update_table()
            self.update_graph()

    def del_item(self, item):
        config_name = self.config_selected
        if config_name in self.config["devices"]:
            del self.config["devices"][config_name]
        self.update_table()
        self.update_graph()

    def update_table(self):
        self.tableWidget.setRowCount(len(self.config["devices"]))
        self.tableWidget.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)
        row_n = 0
        for name, entry in self.config["devices"].items():
            address = str(entry.get("address", ""))
            dtype = entry.get("type", "")
            subbus = entry.get("subbus", "none")
            if not self.config_selected:
                self.config_selected = name
            self.tableWidget.setItem(row_n, 0, QTableWidgetItem(name))
            self.tableWidget.setItem(row_n, 1, QTableWidgetItem(dtype))
            self.tableWidget.setItem(row_n, 2, QTableWidgetItem(address))
            self.tableWidget.setItem(row_n, 3, QTableWidgetItem(subbus))
            row_n += 1
        self.tableWidget.resizeColumnsToContents()
        # self.tableWidget.horizontalHeader().setStretchLastSection(True)

    def table_select(self, item):
        config_name = self.tableWidget.item(item, 0).text()
        self.config_selected = config_name
        self.update_graph()
        self.update_info()

    def update_info(self):
        for name, entry in self.config["devices"].items():
            if name == self.config_selected:
                address = str(entry.get("address", ""))
                dtype = entry.get("type", "")
                subbus = entry.get("subbus", "none")
                info = self.device_types[dtype].get("info", "---")
                self.device_info.setText(f"type: {dtype}\naddr: {address}\nsubbus: {subbus}\n\n{info}\n")
                break

    def update_graph(self):
        gAll = graphviz.Digraph("G", format="svg")
        gAll.attr(rankdir="LR")
        gAll.attr(bgcolor="black")

        iname = self.instance.instances_name

        speed = self.instance.plugin_setup.get("speed", self.instance.OPTIONS["speed"]["default"])
        multiplexer = self.instance.plugin_setup.get("multiplexer", self.instance.OPTIONS["multiplexer"]["default"])
        pin_sda = self.instance.plugin_setup["pins"]["sda"]["pin"]
        pin_scl = self.instance.plugin_setup["pins"]["scl"]["pin"]

        infos = [
            f"{iname}",
            f"sda: {pin_sda}",
            f"scl: {pin_scl}",
            f"speed: {speed/1000:0.1f}kHz",
        ]

        label = f"{{ {{{'|'.join(infos)}}} }}"
        gAll.node(
            f"{iname}",
            shape="record",
            label=label,
            fontsize="11pt",
            style="rounded, filled",
            fillcolor="lightblue",
        )

        order = ["none"]
        if multiplexer:
            for num in range(8):
                order.append(f"{num}")

        mpx_pins = []
        for key in order:
            last = ""
            for name, entry in self.config["devices"].items():
                address = str(entry.get("address", ""))
                dtype = entry.get("type", "")
                subbus = entry.get("subbus", "none")
                if subbus != key:
                    continue

                infos = [
                    f"{dtype}",
                ]

                label = f"{{ {{ {name} ({address}) | {'|'.join(infos)} }} }}"

                color = "lightblue"
                if name == self.config_selected:
                    color = "lightgreen"

                gAll.node(
                    name,
                    shape="record",
                    label=label,
                    fontsize="11pt",
                    style="rounded, filled",
                    fillcolor=color,
                )
                if last:
                    gAll.edge(f"{last}", name, color="white", fontcolor="white")
                elif multiplexer and subbus != "none":
                    gAll.edge(f"mpx:{subbus}", name, color="white", fontcolor="white")
                    mpx_pins.append(subbus)
                else:
                    gAll.edge(f"{iname}", name, color="white", fontcolor="white")
                last = f"{name}"

        if multiplexer:
            subbusses = []
            for num in mpx_pins:
                subbusses.append(f"<{num}>{num}")

            label = f"{{ MPX({multiplexer}) | {{ {'|'.join(subbusses)} }} }}"
            gAll.node(
                "mpx",
                shape="record",
                label=label,
                fontsize="11pt",
                style="rounded, filled",
                fillcolor="lightblue",
            )
            gAll.edge(f"{iname}", "mpx", color="white", fontcolor="white")

        svg_data = gAll.pipe()
        if svg_data:
            self.busgraph.load(svg_data)

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

        hlayout = QHBoxLayout()
        left_layout = QVBoxLayout()
        hlayout.addLayout(left_layout, stretch=0)
        right_layout = QVBoxLayout()
        hlayout.addLayout(right_layout, stretch=1)
        right_layout.addWidget(QLabel("Info:"), stretch=0)
        self.device_info = QLabel("...\n...")
        right_layout.addWidget(self.device_info, stretch=0)
        self.busgraph = MyQSvgWidget()
        right_layout.addWidget(self.busgraph, stretch=1)
        message = QLabel("I2C-Devices:")
        left_layout.addWidget(message, stretch=0)

        self.tableWidget = QTableWidget()
        self.tableWidget.setMinimumWidth(400)
        left_layout.addWidget(self.tableWidget, stretch=1)
        self.tableWidget.setColumnCount(4)
        self.tableWidget.setHorizontalHeaderLabels(["Name", "Type", "Addr", "Subbus"])
        self.tableWidget.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tableWidget.cellClicked.connect(self.table_select)
        left_layout.addWidget(self.tableWidget, stretch=1)

        left_hlayout = QHBoxLayout()
        left_layout.addLayout(left_hlayout)
        right_hlayout = QHBoxLayout()
        right_hlayout.addStretch()
        right_layout.addLayout(right_hlayout)

        button_edit = QPushButton("Edit")
        button_edit.clicked.connect(self.edit_item)
        left_hlayout.addWidget(button_edit, stretch=0)

        button_add = QPushButton("Add")
        button_add.clicked.connect(self.add_item)
        left_hlayout.addWidget(button_add, stretch=0)

        button_del = QPushButton("Remove")
        button_del.clicked.connect(self.del_item)
        left_hlayout.addWidget(button_del, stretch=0)

        dialog.layout.addLayout(hlayout)
        dialog.layout.addWidget(dialog.buttonBox)
        dialog.setLayout(dialog.layout)

        self.update_table()
        self.update_graph()
        self.update_info()

        if dialog.exec():
            self.instance.plugin_setup["config"] = self.config
            return ""
