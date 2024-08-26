#!/usr/bin/env python3
#
#

import argparse
import copy
import glob
import hashlib
import importlib
import json
import yaml
import os
import re
import subprocess
import sys
import time
from functools import partial

import graphviz
import riocore
from riocore import halpins

from riocore import halgraph
from riocore.plugins import Modifiers
from riocore.widgets import MyQSvgWidget, MyStandardItem, edit_float, edit_int, edit_text, edit_bool, edit_combobox, STYLESHEET, STYLESHEET_CHECKBOX_GREEN_RED, STYLESHEET_BUTTON


from PyQt5 import QtSvg
from PyQt5.QtCore import QTimer, QPoint, Qt
from PyQt5.QtGui import QStandardItemModel, QFont, QPixmap
from PyQt5.QtWidgets import (
    QSplitter,
    QMessageBox,
    QHeaderView,
    QGroupBox,
    QLineEdit,
    QApplication,
    QCheckBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QPlainTextEdit,
    QPushButton,
    QScrollArea,
    QTableWidget,
    QTableWidgetItem,
    QTabWidget,
    QTreeView,
    QVBoxLayout,
    QWidget,
)

riocore_path = os.path.dirname(riocore.__file__)


class PinButton(QPushButton):
    def __init__(self, widget, parent=None, pkey=None, bgcolor=None, pin=None):
        super(QPushButton, self).__init__(widget)
        self.parent = parent
        self.pkey = pkey
        self.bgcolor = bgcolor
        if not pin:
            pin = {}
        self.pin = pin
        if self.parent and self.bgcolor:
            self.setStyleSheet(f"background-color: {self.bgcolor}; font-size:12px;")

    def setText(self, text, rotate=False):
        if rotate:
            text = "\n".join(text)
        QPushButton.setText(self, text)

    def enterEvent(self, event):
        if self.parent and self.pkey:
            self.parent.pinlayout_mark(self.pkey)

    def leaveEvent(self, event):
        if self.parent and self.pkey:
            self.parent.pinlayout_mark(":")

    def mark(self, color):
        if self.parent and color:
            self.setStyleSheet(f"background-color: {color}; font-size:12px;")

    def unmark(self):
        if self.parent and self.bgcolor:
            self.setStyleSheet(f"background-color: {self.bgcolor}; font-size:12px;")


class ImageMap(QLabel):
    def __init__(self, parent):
        super(QLabel, self).__init__(parent)
        self.parent = parent

    def mousePressEvent(self, event):
        if event.button() == Qt.RightButton:
            self.setPin(event.pos())

    def setPin(self, pos):
        grid = 5
        pos_x = pos.x()
        pos_y = pos.y()
        used_pos_x = set()
        used_pos_y = set()
        used_pins = []
        for slot in self.parent.slots:
            for pin_name, pin_data in slot["pins"].items():
                if isinstance(pin_data, str):
                    used_pins.append(pin_data)
                else:
                    used_pins.append(pin_data["pin"])
                    if "pos" in pin_data:
                        used_pos_x.add(pin_data["pos"][0])
                        used_pos_y.add(pin_data["pos"][1])

        # align to other positions +-grid size
        for pos in used_pos_x:
            if abs(pos - pos_x) <= grid:
                pos_x = pos
                break
        for pos in used_pos_y:
            if abs(pos - pos_y) <= grid:
                pos_y = pos
                break

        pin_name_default = "P1"
        if self.parent.slots:
            last_slot = self.parent.slots[-1]
            pin_name_num = 1
            found = True
            while found:
                found = False
                for pin_name in last_slot["pins"]:
                    if f"P{pin_name_num}" == pin_name:
                        pin_name_num += 1
                        found = True
            pin_name_default = f"P{pin_name_num}"

        dialog = QDialog()
        dialog.setWindowTitle("set pin")
        dialog.setStyleSheet(STYLESHEET)
        dialog_buttonBox = QDialogButtonBox(QDialogButtonBox.Ok)
        dialog_buttonBox.accepted.connect(dialog.accept)
        dialog.layout = QVBoxLayout()

        message = QLabel("Slot:")
        dialog.layout.addWidget(message)
        slot_select = QComboBox()
        slot_select.setEditable(True)
        for slot in reversed(self.parent.slots):
            slot_select.addItem(slot["name"])
        dialog.layout.addWidget(slot_select)

        message = QLabel("Pin-Name:")
        dialog.layout.addWidget(message)
        pin_name = QLineEdit(pin_name_default)
        dialog.layout.addWidget(pin_name)

        message = QLabel("FPGA-Pin:")
        dialog.layout.addWidget(message)
        pin_select = QComboBox()
        pin_select.setEditable(True)
        for pin in self.parent.pinlist:
            if ":" not in pin and pin not in used_pins:
                pin_select.addItem(pin)
        dialog.layout.addWidget(pin_select)

        message = QLabel("Direction:")
        dialog.layout.addWidget(message)
        direction = QComboBox()
        direction.addItem("all")
        direction.addItem("output")
        direction.addItem("input")
        dialog.layout.addWidget(direction)

        message = QLabel("PosX:")
        dialog.layout.addWidget(message)
        posx = QComboBox()
        posx.setEditable(True)
        posx.addItem(str(pos_x))
        for pos in used_pos_x:
            posx.addItem(str(pos))
        dialog.layout.addWidget(posx)

        message = QLabel("PosY:")
        dialog.layout.addWidget(message)
        posy = QComboBox()
        posy.setEditable(True)
        posy.addItem(str(pos_y))
        for pos in used_pos_y:
            posy.addItem(str(pos))
        dialog.layout.addWidget(posy)

        dialog.layout.addWidget(dialog_buttonBox)
        dialog.setLayout(dialog.layout)

        if dialog.exec():
            slot_name = slot_select.currentText()
            name = pin_name.text()
            pin = pin_select.currentText()
            direction_str = direction.currentText()
            pos_x = posx.currentText()
            pos_y = posy.currentText()
            if direction_str == "":
                direction_str = "all"

            if slot_name and name and pin:
                pin_cfg = {"pin": pin, "pos": [int(pos_x), int(pos_y)], "direction": direction_str}

                slot_n = -1
                for sn, slot in enumerate(self.parent.slots):
                    if slot["name"] == slot_name:
                        slot_n = sn
                        break

                if slot_n == -1:
                    self.parent.slots.append(
                        {
                            "name": slot_name,
                            "comment": "",
                            "default": "",
                            "pins": {name: pin_cfg},
                        }
                    )
                else:
                    self.parent.slots[slot_n]["pins"][name] = pin_cfg

                print(json.dumps(self.parent.slots, indent=4))
                self.parent.request_pin_table_load = 1
            else:
                print("ERROR: missing informations")


class TabLinuxCNC:
    def __init__(self, parent=None):
        self.parent = parent
        self.linuxcnc = {
            "rio.ini": QPlainTextEdit(),
            "rio.hal": QPlainTextEdit(),
            "custom_postgui.hal": QPlainTextEdit(),
            "rio-gui.xml": QPlainTextEdit(),
            "rio.c": QPlainTextEdit(),
        }
        self.linuxcnc_tabwidget = QTabWidget()
        for filename, widget in self.linuxcnc.items():
            widget.clear()
            widget.insertPlainText("")
            self.linuxcnc_tabwidget.addTab(widget, filename)

    def setTab(self, name):
        self.linuxcnc_tabwidget.setCurrentWidget(self.linuxcnc[name])

    def widget(self):
        return self.linuxcnc_tabwidget

    def timer(self):
        pass

    def update(self):
        config_name = self.parent.config.get("name")

        for filename, widget in self.linuxcnc.items():
            file_content = open(f"{self.parent.output_path}/{config_name}/LinuxCNC/{filename}", "r").read()
            widget.clear()
            widget.insertPlainText(file_content)


class TabGateware:
    def __init__(self, parent=None):
        self.parent = parent
        self.gateware = {
            "rio.v": QPlainTextEdit(),
            "Makefile": QPlainTextEdit(),
            "Compile-Output": QPlainTextEdit(),
            "Flash-Output": QPlainTextEdit(),
        }
        self.gateware_tabwidget = QTabWidget()
        for filename, widget in self.gateware.items():
            widget.clear()
            widget.insertPlainText("")
            self.gateware_tabwidget.addTab(widget, filename)

    def setTab(self, name):
        self.gateware_tabwidget.setCurrentWidget(self.gateware[name])

    def widget(self):
        return self.gateware_tabwidget

    def timer(self):
        pass

    def update(self):
        config_name = self.parent.config.get("name")

        for filename, widget in self.gateware.items():
            if not filename.endswith("-Output"):
                file_content = open(f"{self.parent.output_path}/{config_name}/Gateware/{filename}", "r").read()
                widget.clear()
                widget.insertPlainText(file_content)
                if filename == "rio.v":
                    hash_md5 = hashlib.md5()
                    hash_md5.update(file_content.encode())
                    self.parent.gateware_hash = hash_md5.hexdigest()


class TabSignals:
    def __init__(self, parent=None):
        self.parent = parent
        self.sig_table = QTableWidget()
        self.sig_table.setColumnCount(5)
        self.sig_table.setHorizontalHeaderItem(0, QTableWidgetItem("Halname"))
        self.sig_table.setHorizontalHeaderItem(1, QTableWidgetItem("Dir"))
        self.sig_table.setHorizontalHeaderItem(2, QTableWidgetItem("Target"))
        self.sig_table.setHorizontalHeaderItem(3, QTableWidgetItem("Type"))
        self.sig_table.setHorizontalHeaderItem(4, QTableWidgetItem("Comment"))
        self.sig_table.horizontalHeader().sectionClicked.connect(self.onHeaderClickedSignals)
        self.sig_table_sort_col = 1

    def widget(self):
        return self.sig_table

    def timer(self):
        pass

    def update(self):
        self.sig_table.setRowCount(0)
        table_data = []

        def sort_key(a):
            col = a[idx]
            numbers = re.findall(r"\d+", col)
            for number in numbers:
                col = col.replace(number, f"{int(number):09d}")
            return col.lower()

        for module_data in self.parent.config.get("modules", []):
            slot_name = module_data.get("slot")
            for plugin_instance in self.parent.modules[slot_name]["instances"]:
                for signal_name, signal_config in plugin_instance.signals().items():
                    signal_direction = signal_config["direction"]
                    signal_halname = signal_config["halname"]
                    is_bool = signal_config.get("bool", False)
                    htype = "bit" if is_bool else "float"

                    if "userconfig" not in signal_config:
                        signal_config["userconfig"] = {}
                    userconfig = signal_config["userconfig"]

                    if "net" not in userconfig:
                        userconfig["net"] = ""
                    if "function" not in userconfig:
                        userconfig["function"] = ""
                    if "setp" not in userconfig:
                        userconfig["setp"] = ""

                    signal_net = userconfig.get("net", "")
                    signal_function = userconfig.get("function", "")
                    signal_setp = str(userconfig.get("setp", ""))

                    key = "net"
                    if signal_function:
                        key = "function"
                    elif signal_setp:
                        key = "setp"

                    options_net = []
                    for halpin, halpin_info in halpins.LINUXCNC_SIGNALS[signal_direction].items():
                        if is_bool:
                            if halpin_info.get("type") == bool:
                                options_net.append(halpin)
                        elif halpin_info.get("type") != bool:
                            options_net.append(halpin)

                    options_func = []
                    for halpin, halpin_info in halpins.RIO_FUNCTIONS[signal_direction].items():
                        if is_bool:
                            if halpin_info.get("type") == bool:
                                options_func.append(halpin)
                        elif halpin_info.get("type") != bool:
                            options_func.append(halpin)

                    if key == "function":
                        widget = self.parent.edit_item(userconfig, "function", {"type": "select", "options": options_func, "default": ""}, cb=self.sig_edit_cb)
                    elif key == "setp":
                        widget = self.parent.edit_item(userconfig, "setp", {"type": str, "default": ""}, cb=self.sig_edit_cb)
                    else:
                        widget = self.parent.edit_item(userconfig, "net", {"type": "select", "options": options_net, "default": ""}, cb=self.sig_edit_cb)

                    table_data.append(
                        (f"rio.{signal_halname}", {"output": "<-", "input": "->", "inout": "<->"}.get(signal_direction, signal_direction), signal_net, htype, key, plugin_instance, signal_name, widget)
                    )

        for plugin_instance in self.parent.plugins.plugin_instances:
            for signal_name, signal_config in plugin_instance.signals().items():
                signal_direction = signal_config["direction"]
                signal_halname = signal_config["halname"]
                is_bool = signal_config.get("bool", False)
                htype = "bit" if is_bool else "float"

                if "userconfig" not in signal_config:
                    signal_config["userconfig"] = {}
                userconfig = signal_config["userconfig"]
                signal_net = userconfig.get("net", "")
                signal_function = userconfig.get("function", "")
                signal_setp = str(userconfig.get("setp", ""))

                key = "net"
                if signal_function:
                    key = "function"
                elif signal_setp:
                    key = "setp"

                options_net = []
                for halpin, halpin_info in halpins.LINUXCNC_SIGNALS[signal_direction].items():
                    if is_bool:
                        if halpin_info.get("type") == bool:
                            options_net.append(halpin)
                    elif halpin_info.get("type") != bool:
                        options_net.append(halpin)

                options_func = []
                for halpin, halpin_info in halpins.RIO_FUNCTIONS[signal_direction].items():
                    if is_bool:
                        if halpin_info.get("type") == bool:
                            options_func.append(halpin)
                    elif halpin_info.get("type") != bool:
                        options_func.append(halpin)

                if key == "function":
                    widget = self.parent.edit_item(userconfig, "function", {"type": "select", "options": options_func, "default": ""}, cb=self.sig_edit_cb)
                elif key == "setp":
                    widget = self.parent.edit_item(userconfig, "setp", {"type": str, "default": ""}, cb=self.sig_edit_cb)
                else:
                    widget = self.parent.edit_item(userconfig, "net", {"type": "select", "options": options_net, "default": ""}, cb=self.sig_edit_cb)

                table_data.append(
                    (f"rio.{signal_halname}", {"output": "<-", "input": "->", "inout": "<->"}.get(signal_direction, signal_direction), signal_net, htype, key, plugin_instance, signal_name, widget)
                )

        if self.sig_table_sort_col > 0:
            idx = self.sig_table_sort_col - 1
            table_data.sort(key=sort_key)
        elif self.sig_table_sort_col < 0:
            idx = -self.sig_table_sort_col - 1
            table_data.sort(key=sort_key, reverse=True)

        for row_n, row in enumerate(table_data):
            self.sig_table.setRowCount(row_n + 1)
            for col_n, col in enumerate(row[:5]):
                pitem = QTableWidgetItem(col)
                self.sig_table.setItem(row_n, col_n, pitem)
            self.sig_table.setCellWidget(row_n, 2, row[7])

        for row_n, row in enumerate(table_data):
            for col_n, col in enumerate(row[:5]):
                self.sig_table.resizeColumnToContents(col_n)
            break

        self.sig_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)

    def sig_edit_cb(self, widget):
        self.parent.config_load()
        self.parent.generate_cb(preview=True)
        self.parent.request_load_tree = 2
        self.update()
        self.parent.tabs["Json"].update()

    def onHeaderClickedSignals(self, logicalIndex):
        logicalIndex += 1
        if self.sig_table_sort_col == logicalIndex:
            self.sig_table_sort_col = -logicalIndex
        else:
            self.sig_table_sort_col = logicalIndex
        self.update()


class TabPins:
    def __init__(self, parent=None):
        self.parent = parent
        self.pin_table = QTableWidget()
        self.pin_table.setColumnCount(6)
        self.pin_table.setHorizontalHeaderItem(0, QTableWidgetItem("Pin"))
        self.pin_table.setHorizontalHeaderItem(1, QTableWidgetItem("Plugin"))
        self.pin_table.setHorizontalHeaderItem(2, QTableWidgetItem("Pin-Name"))
        self.pin_table.setHorizontalHeaderItem(3, QTableWidgetItem("Mapping"))
        self.pin_table.setHorizontalHeaderItem(4, QTableWidgetItem("Direction"))
        self.pin_table.setHorizontalHeaderItem(5, QTableWidgetItem("Comment"))
        self.pin_table.horizontalHeader().sectionClicked.connect(self.onHeaderClickedPins)
        self.pin_table_sort_col = 1

    def widget(self):
        return self.pin_table

    def timer(self):
        pass

    def update(self):
        self.pin_table.setRowCount(0)
        in_use = set()
        table_data = []
        for plugin_instance in self.parent.plugins.plugin_instances:
            name = plugin_instance.plugin_setup.get("name")
            title = plugin_instance.NAME
            if name:
                title = f"{name} ({plugin_instance.NAME})"

            for pin_name, pin_defaults in plugin_instance.PINDEFAULTS.items():
                pin_setup = plugin_instance.plugin_setup.get("pins", {}).get(pin_name, {})
                if not pin_setup and pin_defaults.get("optional") is True:
                    continue
                if "pin" not in pin_setup and pin_defaults.get("optional") is True:
                    continue
                pin = pin_setup.get("pin")
                if not pin:
                    continue
                pin_real = pin

                mapped = ""
                if pin in self.parent.pinmapping_rev:
                    pin_real = pin
                    mapped = self.parent.pinmapping_rev[pin]
                elif pin in self.parent.pinmapping:
                    pin_real = self.parent.pinmapping[pin]
                    mapped = pin

                comment = ""
                modifiers = pin_setup.get("modifier")
                if modifiers:
                    mlist = set()
                    for modifier in modifiers:
                        mlist.add(modifier["type"])
                    comment = f"{','.join(mlist)}"
                in_use.add(pin_real)

                widget = self.parent.edit_item(pin_setup, "pin", {"type": "select", "options": self.parent.pinlist, "default": ""}, cb=None)
                table_data.append((pin_real, title, pin_name, mapped, pin_defaults["direction"], comment, widget))

        for module_data in self.parent.config.get("modules", []):
            slot_name = module_data.get("slot")
            module_name = module_data.get("module")
            title = slot_name
            if module_name:
                title = f"{module_name} ({title})"

            for plugin_instance in self.parent.modules[slot_name]["instances"]:
                name = plugin_instance.plugin_setup.get("name")
                title = plugin_instance.NAME
                if name:
                    title = f"{name} ({plugin_instance.NAME})"

                for pin_name, pin_defaults in plugin_instance.PINDEFAULTS.items():
                    pin_setup = plugin_instance.plugin_setup.get("pins", {}).get(pin_name, {})
                    if not pin_setup and pin_defaults.get("optional") is True:
                        continue
                    if "pin" not in pin_setup and pin_defaults.get("optional") is True:
                        continue

                    pin = pin_setup.get("pin", pin_setup.get("pin_mapped", "???"))
                    pin = f"{slot_name}:{pin}"
                    pin_real = pin

                    mapped = ""
                    if pin in self.parent.pinmapping_rev:
                        pin_real = pin
                        mapped = self.parent.pinmapping_rev[pin]
                    elif pin in self.parent.pinmapping:
                        pin_real = self.parent.pinmapping[pin]
                        mapped = pin

                    comment = ""
                    modifiers = pin_setup.get("modifier")
                    if modifiers:
                        mlist = set()
                        for modifier in modifiers:
                            mlist.add(modifier["type"])
                        comment = f"{','.join(mlist)}"
                    in_use.add(pin_real)

                    table_data.append((pin_real, title, pin_name, mapped, pin_defaults["direction"], comment, None))

        for pin in self.parent.pinlist:
            if pin not in in_use:
                if pin in self.parent.pinmapping:
                    continue
                if pin in self.parent.pinmapping_rev:
                    if self.parent.pinmapping_rev[pin] in in_use:
                        continue
                in_use.add(pin)
                table_data.append((pin, "", "", "", "", "unused", None))

        def sort_key(a):
            col = a[idx]
            if not col:
                return ""
            numbers = re.findall(r"\d+", col)
            for number in numbers:
                col = col.replace(number, f"{int(number):09d}")
            return col.lower()

        if self.pin_table_sort_col > 0:
            idx = self.pin_table_sort_col - 1
            table_data.sort(key=sort_key)
        elif self.pin_table_sort_col < 0:
            idx = -self.pin_table_sort_col - 1
            table_data.sort(key=sort_key, reverse=True)

        for row_n, row in enumerate(table_data):
            self.pin_table.setRowCount(row_n + 1)
            for col_n, col in enumerate(row[:6]):
                pitem = QTableWidgetItem(col)
                self.pin_table.setItem(row_n, col_n, pitem)
                self.pin_table.resizeColumnToContents(col_n)
            self.pin_table.setCellWidget(row_n, 3, row[6])

        for col_n, col in enumerate(row[:6]):
            self.pin_table.resizeColumnToContents(col_n)
        self.pin_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)

    def onHeaderClickedPins(self, logicalIndex):
        logicalIndex += 1
        if self.pin_table_sort_col == logicalIndex:
            self.pin_table_sort_col = -logicalIndex
        else:
            self.pin_table_sort_col = logicalIndex
        self.update()


class TabHal:
    def __init__(self, parent=None):
        self.parent = parent
        self.hal_img = MyQSvgWidget()

    def widget(self):
        return self.hal_img

    def timer(self):
        pass

    def update(self):
        config_name = self.parent.config.get("name")
        svg_data = halgraph.HalGraph(f"{self.parent.output_path}/{config_name}/LinuxCNC/rio.ini").svg()
        self.hal_img.load(svg_data)


class TabOverview:
    def __init__(self, parent=None):
        self.parent = parent
        self.overview_img = MyQSvgWidget()

    def widget(self):
        return self.overview_img

    def timer(self):
        pass

    def update(self):
        num = 0
        fpga_name = f"{self.parent.config.get('boardcfg')}"

        gAll = graphviz.Digraph("G", format="svg")
        gAll.attr(rankdir="LR")
        gAll.attr(bgcolor="black")

        lcports = []
        sports = []

        # show slots
        for slot in self.parent.slots:
            slot_name = slot.get("name")
            slot_pins = slot.get("pins", {})
            mportsl = []
            mportsr = []
            for pin_name, pin in slot_pins.items():
                if isinstance(pin, dict):
                    pin = pin["pin"]
                pin_id = f"{slot_name}_{pin_name}"
                mportsl.append(f"<{pin}>{pin}")
                mportsr.append(f"<{pin_id}>{pin_name}")

            label = f"{{ {{{' | '.join(mportsl)}}} | {slot_name} | {{{' | '.join(mportsr)}}} }}"
            sports.append(label)

        joint_n = 0
        for plugin_instance in self.parent.plugins.plugin_instances:
            pports = []
            name = plugin_instance.plugin_setup.get("name", plugin_instance.title)
            title = plugin_instance.NAME
            if name:
                title = f"{name} ({plugin_instance.NAME})"

            if plugin_instance.TYPE == "expansion":
                title = plugin_instance.expansion_prefix

            for pin_name, pin_defaults in plugin_instance.PINDEFAULTS.items():
                pin_setup = plugin_instance.plugin_setup.get("pins", {}).get(pin_name, {})
                pports.append(f"<{pin_name}>{pin_name}")
                if not pin_setup and pin_defaults.get("optional") is True:
                    continue
                if "pin" not in pin_setup and pin_defaults.get("optional") is True:
                    continue
                pin = pin_setup.get("pin")
                if not pin:
                    continue

                con_dev = fpga_name
                con_pin = pin

                if pin and pin in self.parent.expansion_pins:
                    con_dev = "_".join(pin.split("_")[0:-1])
                    con_pin = pin.replace("[", "").replace("]", "")

                if ":" in con_pin:
                    con_pin = con_pin.replace(":", "_")

                if pin_defaults["direction"] == "input":
                    modifiers = pin_setup.get("modifier", [])
                    color = "green"
                    arrow_dir = "forward"
                else:
                    modifiers = pin_setup.get("modifier", [])
                    if modifiers:
                        modifiers = reversed(modifiers)
                    color = "red"
                    arrow_dir = "back"

                if modifiers:
                    modifier_chain = []
                    for modifier_num, modifier in enumerate(modifiers):
                        modifier_type = modifier["type"]
                        modifier_chain.append(modifier_type)
                    modifier_label = f"{{ <l> | {' | '.join(modifier_chain)} | <r> }}"
                    gAll.edge(f"{con_dev}:{con_pin}", f"{name}_{pin_name}_{modifier_type}_{modifier_num}:l", dir=arrow_dir, color=color)
                    con_dev = f"{name}_{pin_name}_{modifier_type}_{modifier_num}"
                    con_pin = "r"
                    gAll.node(
                        f"{name}_{pin_name}_{modifier_type}_{modifier_num}",
                        shape="record",
                        label=modifier_label,
                        fontsize="11pt",
                        style="rounded, filled",
                        fillcolor="lightyellow",
                    )

                gAll.edge(f"{con_dev}:{con_pin}", f"{title}:{pin_name}", dir=arrow_dir, color=color)

                if pin and ":" not in pin and pin not in self.parent.expansion_pins:
                    sports.append(f"<{pin}>{pin}")

                num += 1

            signalports = []
            for signal_name, signal_config in plugin_instance.plugin_setup.get("signals", {}).items():
                net = signal_config.get("net")
                function = signal_config.get("function")
                signalports.append(f"<signal_{signal_name}>{signal_name}")
                signal_direction = plugin_instance.SIGNALS.get(signal_name, {}).get("direction")
                direction_mapping = {"input": "normal", "output": "back", "inout": "both"}

                if not net and not function and plugin_instance.plugin_setup.get("is_joint", False):
                    if signal_name == "position" and signal_direction == "input":
                        hal_pin = f"joint.{joint_n}.motor-pos-fb"
                        gAll.edge(f"{title}:signal_{signal_name}", f"hal:{hal_pin}", dir="normal", color="white", fontcolor="white")
                        lcports.append(f"<{hal_pin}>{hal_pin}")
                    elif signal_name == "position" and signal_direction == "output":
                        hal_pin = f"joint.{joint_n}.motor-pos-cmd"
                        gAll.edge(f"{title}:signal_{signal_name}", f"hal:{hal_pin}", dir="back", color="white", fontcolor="white")
                        lcports.append(f"<{hal_pin}>{hal_pin}")
                    elif signal_name == "velocity":
                        hal_pin = f"joint.{joint_n}.motor-pos-cmd"
                        gAll.edge(f"{title}:signal_{signal_name}", f"hal:{hal_pin}", dir="back", color="white", fontcolor="white")
                        lcports.append(f"<{hal_pin}>{hal_pin}")

                if function:
                    gAll.edge(f"{title}:signal_{signal_name}", f"hal:{function}", dir=direction_mapping.get(signal_direction, "none"), color="white", fontcolor="white")
                    lcports.append(f"<{function}>{function}")
                if net:
                    gAll.edge(f"{title}:signal_{signal_name}", f"hal:{net}", dir=direction_mapping.get(signal_direction, "none"), color="white", fontcolor="white")
                    lcports.append(f"<{net}>{net}")

            if plugin_instance.TYPE == "expansion":
                eports = []
                for pname in plugin_instance.expansion_outputs():
                    eports.append(f"<{pname.replace('[', '').replace(']', '')}>{pname}")
                for pname in plugin_instance.expansion_inputs():
                    eports.append(f"<{pname.replace('[', '').replace(']', '')}>{pname}")

                label = f"{{ {{{' | '.join(pports)}}} | {title} | {{{' | '.join(eports)}}} }}"

            elif signalports:
                label = f"{{ {{{' | '.join(pports)}}} | {title} | {{{' | '.join(signalports)}}} }}"
            else:
                label = f"{{ {{{' | '.join(pports)}}} | {title} }}"

            gAll.node(
                title,
                shape="record",
                label=label,
                fontsize="11pt",
                style="rounded, filled",
                fillcolor="lightblue",
            )

            if plugin_instance.plugin_setup.get("is_joint", False):
                joint_n += 1

        for module_data in self.parent.config.get("modules", []):
            slot_name = module_data.get("slot")
            module_name = module_data.get("module")
            title = slot_name
            if module_name:
                title = f"{module_name} ({title})"

            for plugin_instance in self.parent.modules[slot_name]["instances"]:
                pports = []
                name = plugin_instance.plugin_setup.get("name")
                title = plugin_instance.NAME
                if name:
                    title = f"{name} ({plugin_instance.NAME})"
                for pin_name, pin_defaults in plugin_instance.PINDEFAULTS.items():
                    pin_setup = plugin_instance.plugin_setup.get("pins", {}).get(pin_name, {})
                    if "pin_mapped" not in pin_setup:
                        continue

                    pin = f"{slot_name}_{pin_setup['pin_mapped']}"
                    con_dev = fpga_name
                    con_pin = pin

                    if pin and pin in self.parent.expansion_pins:
                        con_dev = "_".join(pin.split("_")[0:-1])
                        con_pin = pin.replace("[", "").replace("]", "")

                    if pin_defaults["direction"] == "input":
                        modifiers = pin_setup.get("modifier", [])
                        color = "green"
                        arrow_dir = "forward"
                    else:
                        modifiers = pin_setup.get("modifier", [])
                        if modifiers:
                            modifiers = reversed(modifiers)
                        color = "red"
                        arrow_dir = "back"

                    if modifiers:
                        modifier_chain = []
                        for modifier_num, modifier in enumerate(modifiers):
                            modifier_type = modifier["type"]
                            modifier_chain.append(modifier_type)
                        modifier_label = f"{{ <l> | {' | '.join(modifier_chain)} | <r> }}"
                        gAll.edge(f"{con_dev}:{con_pin}", f"{name}_{pin_name}_{modifier_type}_{modifier_num}:l", dir=arrow_dir, color=color)
                        con_dev = f"{name}_{pin_name}_{modifier_type}_{modifier_num}"
                        con_pin = "r"
                        gAll.node(
                            f"{name}_{pin_name}_{modifier_type}_{modifier_num}",
                            shape="record",
                            label=modifier_label,
                            fontsize="11pt",
                            style="rounded, filled",
                            fillcolor="lightyellow",
                        )

                    gAll.edge(f"{con_dev}:{con_pin}", f"{title}:{pin_name}", dir=arrow_dir, color=color)
                    pports.append(f"<{pin_name}>{pin_name}")

                signalports = []
                for signal_name, signal_config in plugin_instance.plugin_setup.get("signals", {}).items():
                    net = signal_config.get("net")
                    function = signal_config.get("function")
                    signalports.append(f"<signal_{signal_name}>{signal_name}")
                    signal_direction = plugin_instance.SIGNALS.get(signal_name, {}).get("direction")
                    direction_mapping = {"input": "forward", "output": "back", "inout": "both"}

                    if not net and not function and plugin_instance.plugin_setup.get("is_joint", False):
                        if signal_name == "position" and signal_direction == "input":
                            hal_pin = f"joint.{joint_n}.motor-pos-fb"
                            gAll.edge(f"{title}:signal_{signal_name}", f"hal:{hal_pin}", dir="normal", color="white", fontcolor="white")
                            lcports.append(f"<{hal_pin}>{hal_pin}")
                        elif signal_name == "position" and signal_direction == "output":
                            hal_pin = f"joint.{joint_n}.motor-pos-cmd"
                            gAll.edge(f"{title}:signal_{signal_name}", f"hal:{hal_pin}", dir="back", color="white", fontcolor="white")
                            lcports.append(f"<{hal_pin}>{hal_pin}")
                        elif signal_name == "velocity":
                            hal_pin = f"joint.{joint_n}.motor-pos-cmd"
                            gAll.edge(f"{title}:signal_{signal_name}", f"hal:{hal_pin}", dir="back", color="white", fontcolor="white")
                            lcports.append(f"<{hal_pin}>{hal_pin}")

                    if function:
                        gAll.edge(f"{title}:signal_{signal_name}", f"hal:{function}", dir=direction_mapping.get(signal_direction, "none"), color="white", fontcolor="white")
                        lcports.append(f"<{function}>{function}")
                    if net:
                        gAll.edge(f"{title}:signal_{signal_name}", f"hal:{net}", dir=direction_mapping.get(signal_direction, "none"), color="white", fontcolor="white")
                        lcports.append(f"<{net}>{net}")

                if signalports:
                    label = f"{{ {{{' | '.join(pports)}}} | {title} | {{{' | '.join(signalports)}}} }}"
                else:
                    label = f"{{ {{{' | '.join(pports)}}} | {title} }}"
                gAll.node(
                    title,
                    shape="record",
                    label=label,
                    fontsize="11pt",
                    style="rounded, filled",
                    fillcolor="lightblue",
                )

                if plugin_instance.plugin_setup.get("is_joint", False):
                    joint_n += 1

        label = f"{{ {{ {fpga_name}\\nPhysical-Pins | {' | '.join(sports)}}} }}"
        gAll.node(f"{fpga_name}", shape="record", label=label, fontsize="11pt", style="rounded, filled", fillcolor="yellow")

        label = f"{{ {{ LinuxCNC\\nHAL-Pins | {' | '.join(lcports)}}} }}"
        gAll.node(
            "hal",
            shape="record",
            label=label,
            fontsize="11pt",
            style="rounded, filled",
            fillcolor="lightgreen",
        )

        self.overview_img.load(gAll.pipe())
        # self.overview_img.setFixedSize(self.overview_img.renderer().defaultSize())


class TabJson:
    def __init__(self, parent=None):
        self.parent = parent
        self.jsonpreview = QPlainTextEdit()
        self.jsonpreview.clear()
        self.jsonpreview.insertPlainText("...")
        # self.jsonpreview.verticalScrollBar().setValue(0)

    def widget(self):
        return self.jsonpreview

    def timer(self):
        pass

    def update(self):
        config = self.parent.clean_config(self.parent.config)
        self.jsonpreview.clear()
        self.jsonpreview.insertPlainText(json.dumps(config, indent=4))
        # self.jsonpreview.verticalScrollBar().setValue(0)


class TabBoard:
    def __init__(self, parent=None):
        self.parent = parent
        self.img_container = QWidget()
        self.img_layout = QVBoxLayout(self.img_container)
        self.boardimg = QWidget()
        self.img_layout.addWidget(self.boardimg)

        self.pininfo = QLabel("")
        self.pininfo_timer = 0

        ipin_layout = QVBoxLayout()
        self.ipin_widget = QWidget()
        self.ipin_widget.setLayout(ipin_layout)
        ipin_layout.addWidget(self.img_container)
        ipin_layout.addWidget(self.pininfo)
        ipin_layout.addStretch()

    def widget(self):
        return self.ipin_widget

    def timer(self):
        if self.pininfo_timer == 1:
            self.pininfo_timer = 0
            self.pininfo.setText("")
        elif self.pininfo_timer > 1:
            self.pininfo_timer -= 1

    def update(self):
        self.img_layout.removeWidget(self.boardimg)
        self.boardimg = QWidget()
        self.pinlabels = {}

        pinimage = self.parent.board.get("pinimage", "board.png")
        pinimage_path = f"{self.parent.boardcfg_path}/{pinimage}"
        if not pinimage or not os.path.isfile(pinimage_path):
            if self.tabwidget.tabText(0) == "Board":
                self.tabwidget.removeTab(0)
            return

        pinlayout_pixmap = QPixmap(pinimage_path)
        self.boardimg.setFixedSize(pinlayout_pixmap.size())

        pinlayout_image = ImageMap(self.parent)
        pinlayout_image.setAlignment(Qt.AlignRight | Qt.AlignTop)
        pinlayout_image.setFixedSize(pinlayout_pixmap.size())
        pinlayout_image.setPixmap(pinlayout_pixmap)

        self.img_layout.addWidget(self.boardimg)

        layout_box = QVBoxLayout(self.boardimg)
        layout_box.setContentsMargins(0, 0, 0, 0)
        layout_box.addWidget(pinlayout_image)

        for slot in self.parent.slots:
            slot_name = slot["name"]
            module_name = self.parent.get_module_by_slot(slot_name)

            if "rect" in slot:
                pkey = f"{slot_name}:"
                w = int(slot["rect"][2])
                h = int(slot["rect"][3])
                tooltip = f"slot:{slot_name}"
                bgcolor = "lightblue"
                if module_name:
                    bgcolor = "lightgreen"
                    tooltip += f"\nmodule: {module_name}"
                self.pinlabels[pkey] = PinButton(self.boardimg, parent=self, pkey=pkey, bgcolor=bgcolor)
                self.pinlabels[pkey].setFixedWidth(w)
                self.pinlabels[pkey].setFixedHeight(h)
                self.pinlabels[pkey].setText(pkey)
                self.pinlabels[pkey].move(QPoint(int(slot["rect"][0]), int(slot["rect"][1])))
                self.pinlabels[pkey].setToolTip(tooltip)
                if module_name:
                    self.pinlabels[pkey].clicked.connect(partial(self.remove_module, slot_name))
                else:
                    self.pinlabels[pkey].clicked.connect(partial(self.parent.add_module, slot_name=slot_name, slot_select=False))

            for pin_id, pin in slot["pins"].items():
                if isinstance(pin, dict):
                    # check if pin is allready used
                    pkey = f"{slot_name}:{pin_id}"

                    bgcolor = "blue"
                    if "pos" in pin:
                        tooltip = f"{slot_name}:{pin_id} {pin['pin']} ({pin.get('direction', 'all')})"
                    else:
                        tooltip = f"{slot_name}"

                    plugin_instance, pin_name = self.parent.get_plugin_by_pin(pin["pin"])
                    if module_name:
                        bgcolor = "green"
                        tooltip += f"\nmodule: {module_name}"
                    elif plugin_instance:
                        bgcolor = "green"
                        tooltip += f"\n{plugin_instance.title} ({plugin_instance.NAME}) : {pin_name}"

                    if "pos" in pin:
                        self.pinlabels[pkey] = PinButton(self.boardimg, parent=self, pkey=pkey, bgcolor=bgcolor, pin=pin)
                        if pin.get("rotate"):
                            if len(pin["pos"]) == 4:
                                self.pinlabels[pkey].setFixedWidth(int(pin["pos"][2]))
                                self.pinlabels[pkey].setFixedHeight(int(pin["pos"][3]))
                            else:
                                self.pinlabels[pkey].setFixedWidth(15)
                                self.pinlabels[pkey].setFixedHeight(len(pin_id * 15))
                            self.pinlabels[pkey].setText(pin_id, True)
                        else:
                            if len(pin["pos"]) == 4:
                                self.pinlabels[pkey].setFixedWidth(int(pin["pos"][2]))
                                self.pinlabels[pkey].setFixedHeight(int(pin["pos"][3]))
                            else:
                                self.pinlabels[pkey].setFixedWidth(len(pin_id * 10))
                                self.pinlabels[pkey].setFixedHeight(15)
                            self.pinlabels[pkey].setText(pin_id)
                        self.pinlabels[pkey].move(QPoint(int(pin["pos"][0]), int(pin["pos"][1])))
                        self.pinlabels[pkey].setToolTip(tooltip)

                        if module_name:
                            self.pinlabels[pkey].clicked.connect(partial(self.remove_module, slot_name))
                        elif plugin_instance:
                            self.pinlabels[pkey].clicked.connect(partial(self.parent.edit_plugin, plugin_instance, plugin_instance.plugin_id, None))
                        else:
                            self.pinlabels[pkey].clicked.connect(partial(self.parent.add_plugin, pin_id, slot_name=slot_name))

                    elif "pos" in slot:
                        self.pinlabels[pkey] = PinButton(self.boardimg, parent=self, pkey=pkey, bgcolor=bgcolor, pin=pin)
                        self.pinlabels[pkey].setFixedWidth(len(slot_name * 10))
                        self.pinlabels[pkey].setFixedHeight(15)
                        self.pinlabels[pkey].setText(slot_name)
                        self.pinlabels[pkey].move(QPoint(int(slot["pos"][0]), int(slot["pos"][1])))
                        self.pinlabels[pkey].setToolTip(tooltip)

                        if module_name:
                            self.pinlabels[pkey].clicked.connect(partial(self.remove_module, slot_name))
                        elif plugin_instance:
                            self.pinlabels[pkey].clicked.connect(partial(self.parent.edit_plugin, plugin_instance))
                        else:
                            self.pinlabels[pkey].clicked.connect(partial(self.parent.add_plugin, pin_id, slot_name=slot_name))

    def remove_module(self, slot_name):
        module_name = self.parent.get_module_by_slot(slot_name)
        qm = QMessageBox
        ret = qm.question(self.parent, "remove module", f"Are you sure to remove module '{module_name}' from slot '{slot_name}' ?", qm.Yes | qm.No)
        if ret == qm.Yes:
            if "modules" in self.parent.config:
                for mn, module in enumerate(self.parent.config["modules"]):
                    if module["slot"] == slot_name:
                        self.parent.config["modules"].pop(mn)
                        break
            del self.parent.modules[slot_name]
            self.parent.load_tree()
            self.parent.tabs["Board"].update()
            self.parent.tabs["Pins"].update()
            self.parent.tabs["Signals"].update()
            self.parent.display()

    def pinlayout_mark(self, pkey):
        slot_name = pkey.split(":")[0]
        infotext = [f"Slot: {slot_name}"]
        infotext.append("Pins:")
        networks = []

        for key, label in self.pinlabels.items():
            splitted = key.split(":")
            if splitted[0] == slot_name:
                color = "darkCyan"
                label.mark(color)
                direction = label.pin.get("direction") or "all"

                plugin_instance, pin_name = self.parent.get_plugin_by_pin(label.pin.get("pin", {}))
                pinfo = ""
                if plugin_instance:
                    pinfo = f"-> {plugin_instance.title} ({plugin_instance.NAME}) : {pin_name}"

                    for signal_name, signal_config in plugin_instance.signals().items():
                        if "userconfig" not in signal_config:
                            signal_config["userconfig"] = {}
                        userconfig = signal_config["userconfig"]
                        net = userconfig.get("net")
                        if net:
                            networks.append(net)

                if key == pkey:
                    pinfo += " <-"

                infotext.append(f" {splitted[1]}: {label.pin.get('pin', {})} ({direction}) {pinfo}")
            else:
                label.unmark()

        if len(infotext) > 2:
            if networks:
                infotext.append("Networks:")
                for net in networks:
                    infotext.append(f" {net}")
            self.pininfo.setText("\n".join(infotext))
            self.pininfo_timer = 0
        else:
            self.pininfo_timer = 3


class WinForm(QWidget):
    def __init__(self, args, parent=None):
        super(WinForm, self).__init__(parent)
        self.setWindowTitle("LinuxCNC-RIO - Setup-GUI")
        # self.showMaximized()
        # self.setMinimumWidth(1400)
        # self.setMinimumHeight(900)
        self.setStyleSheet(STYLESHEET)

        self.listFile = QListWidget()
        layout = QVBoxLayout()
        self.setLayout(layout)

        splitter = QSplitter(Qt.Horizontal)
        layout.addWidget(splitter)

        self.treeview = QTreeView()
        splitter.addWidget(self.treeview)
        # self.treeview.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.model = QStandardItemModel()
        self.model.setHorizontalHeaderLabels(["Name", "Value"])
        self.model.itemChanged.connect(self.itemChanged)
        self.treeview.setModel(self.model)
        self.treeview.setUniformRowHeights(True)

        if not args.config:
            self.config_file = None
            boardcfg = self.select_board()
            if boardcfg:
                self.config = {
                    "name": boardcfg,
                    "boardcfg": boardcfg,
                    "plugins": [],
                }
            elif self.config_file is None:
                exit(1)
        else:
            if os.path.isfile(args.config):
                self.config_file = args.config
            elif os.path.isfile(f"{riocore_path}/configs/{args.config}"):
                self.config_file = f"{riocore_path}/configs/{args.config}"
            else:
                print(f"can not load: {args.config}")
                exit(1)

        self.tabwidget = QTabWidget()
        splitter.addWidget(self.tabwidget)

        self.gateware_hash = None
        self.compile_sub = None
        self.compile_start = 0
        self.flash_sub = None
        self.flash_start = 0

        self.tabs = {
            "Board": TabBoard(self),
            "Overview": TabOverview(self),
            "Hal": TabHal(self),
            "Pins": TabPins(self),
            "Signals": TabSignals(self),
            "Json": TabJson(self),
            "LinuxCNC": TabLinuxCNC(self),
            "Gateware": TabGateware(self),
        }

        for title, tab in self.tabs.items():
            self.tabwidget.addTab(tab.widget(), title)

        container = QWidget()
        button_layout = QHBoxLayout(container)
        layout.addWidget(container)

        info_container = QWidget()
        info_layout = QHBoxLayout(info_container)
        self.info_widget = QLabel("loading...")
        layout.addWidget(info_container)

        info_layout.addWidget(self.info_widget)
        info_layout.addStretch()

        self.info_saved = QCheckBox("Saved")
        self.info_saved.setStyleSheet(STYLESHEET_CHECKBOX_GREEN_RED)
        info_layout.addWidget(self.info_saved)
        self.info_saved.setChecked(True)

        self.info_generated = QCheckBox("Generated")
        self.info_generated.setStyleSheet(STYLESHEET_CHECKBOX_GREEN_RED)
        info_layout.addWidget(self.info_generated)
        self.info_generated.setChecked(False)

        self.info_compiled = QCheckBox("Compiled")
        self.info_compiled.setStyleSheet(STYLESHEET_CHECKBOX_GREEN_RED)
        info_layout.addWidget(self.info_compiled)
        self.info_compiled.setChecked(False)

        self.info_flashed = QCheckBox("Flashed")
        self.info_flashed.setStyleSheet(STYLESHEET_CHECKBOX_GREEN_RED)
        info_layout.addWidget(self.info_flashed)
        self.info_flashed.setChecked(False)

        self.button_save = QPushButton("Save")
        self.button_save.clicked.connect(self.save_config_cb)
        self.button_save.setStyleSheet(STYLESHEET_BUTTON)
        button_layout.addWidget(self.button_save)

        self.button_save_as = QPushButton("Save as")
        self.button_save_as.clicked.connect(self.save_config_as)
        self.button_save_as.setStyleSheet(STYLESHEET_BUTTON)
        button_layout.addWidget(self.button_save_as)

        self.button_generate = QPushButton("Generate")
        self.button_generate.clicked.connect(self.generate_cb)
        self.button_generate.setStyleSheet(STYLESHEET_BUTTON)
        button_layout.addWidget(self.button_generate)

        self.button_compile = QPushButton("Compile")
        self.button_compile.clicked.connect(self.compile_cb)
        self.button_compile.setStyleSheet(STYLESHEET_BUTTON)
        button_layout.addWidget(self.button_compile)

        self.button_flash = QPushButton("Flash")
        self.button_flash.clicked.connect(self.flash_cb)
        self.button_flash.setStyleSheet(STYLESHEET_BUTTON)
        button_layout.addWidget(self.button_flash)

        button = QPushButton("reload tree")
        button.clicked.connect(self.load_tree)
        button_layout.addWidget(button)

        button = QPushButton("reload config")
        button.clicked.connect(self.json_load)
        button_layout.addWidget(button)

        button = QPushButton("test-gui")
        button.clicked.connect(self.testgui)
        button_layout.addWidget(button)

        button = QPushButton("PyVCP-Preview")
        button.clicked.connect(self.open_pyvcp)
        button_layout.addWidget(button)

        self.addons = {}
        for addon_path in sorted(glob.glob(f"{riocore_path}/generator/addons/*/config.py")):
            addon_name = addon_path.split("/")[-2]
            self.addons[addon_name] = importlib.import_module(".config", f"riocore.generator.addons.{addon_name}")

        self.json_load()
        self.config_original = self.clean_config(self.config)
        self.config_checked = {}

        self.request_load_tree = 0
        self.request_generate = 0
        self.request_pin_table_load = 0
        self.request_sig_table_load = 0

        self.treeview.expandAll()
        self.treeview.resizeColumnToContents(0)
        self.treeview.resizeColumnToContents(1)
        self.treeview.collapseAll()
        self.tree_expand("/Plugins/")

        tree_width = self.treeview.header().sectionSize(0) + self.treeview.header().sectionSize(1)
        img_width = max(self.tabs["Board"].widget().width(), 400)
        win_height = max(self.height(), 900)
        self.resize(tree_width + img_width + 100, win_height)
        self.treeview.resize(tree_width, win_height)
        splitter.setSizes((tree_width, img_width))

        self.generate_cb(preview=True)
        self.check_status()
        self.timer = QTimer()
        self.timer.timeout.connect(self.runTimer)
        self.timer.start(1000)

    def select_board(self):
        def load_config_from():
            file_dialog = QFileDialog(self)
            suffix_list = ["*.json"]
            name = file_dialog.getOpenFileName(
                self,
                "Load Config",
                f"{riocore_path}/configs/",
                f"config ( {' '.join(suffix_list)} )" "Load Config",
                "",
            )
            if name[0]:
                dialog.close()
                self.config_file = name[0]

        def show_board_info(idx):
            board_path = board_list[idx]
            if board_path.endswith(".json"):
                board_name = board_path.split("/")[-1].replace(".json", "")
            else:
                board_name = board_path.split("/")[-1]
                board_path = f"{board_path}/board.json"

            board_raw = open(board_path, "r").read()
            board_config = json.loads(board_raw)

            pinimage = board_config.get("pinimage", "board.png")
            image_path = f"{board_path}/{pinimage}"
            if os.path.isfile(image_path):
                pixmap = QPixmap(image_path).scaled(320, 240, Qt.KeepAspectRatio)
                image_label.setPixmap(pixmap)
            else:
                image_label.clear()

            name_label.setText(board_name)
            description = []
            for key in ("name", "description", "type", "family", "toolchain"):
                value = board_config.get(key)
                description.append(f"{key.title()}: {value}")
            description_label.setText("\n".join(description))
            dialog.selected = board_name

        dialog = QDialog()
        dialog.setWindowTitle("create new config / select board")
        dialog.setStyleSheet(STYLESHEET)
        # dialog.setMinimumWidth(800)
        dialog.setMinimumHeight(480)

        dialog.layout = QVBoxLayout()
        dialog.setLayout(dialog.layout)

        dialog_buttonBox = QDialogButtonBox(QDialogButtonBox.Cancel | QDialogButtonBox.Ok)
        dialog_buttonBox.accepted.connect(dialog.accept)
        dialog_buttonBox.rejected.connect(dialog.reject)
        load_button = QPushButton(self.tr("Load existing config"))
        load_button.clicked.connect(load_config_from)
        dialog_buttonBox.addButton(load_button, QDialogButtonBox.ActionRole)

        board_table = QTableWidget()
        board_table.setColumnCount(1)
        board_table.setHorizontalHeaderItem(0, QTableWidgetItem("Boards"))
        header = board_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)

        board_list = []
        board_n = 0
        for path in sorted(glob.glob(f"{riocore_path}/boards/*")):
            if path.endswith(".json"):
                board_name = path.split("/")[-1].replace(".json", "")
            else:
                if not os.path.isfile(f"{path}/board.json"):
                    print(f"WARNING: can not found board.json in {path}")
                    continue
                board_name = path.split("/")[-1]
            board_table.setRowCount(board_n + 1)
            board_list.append(path)
            pitem = QTableWidgetItem(board_name)
            board_table.setItem(board_n, 0, pitem)
            board_n += 1

        board_table.setFixedWidth(300)
        board_table.cellClicked.connect(show_board_info)
        board_table.currentCellChanged.connect(show_board_info)

        mid_layout = QVBoxLayout()
        mid_widget = QWidget()
        mid_widget.setFixedWidth(400)
        mid_widget.setLayout(mid_layout)
        name_label = QLabel("name")
        name_label_font = QFont()
        name_label_font.setBold(True)
        name_label.setFont(name_label_font)

        mid_layout.addWidget(name_label)
        description_label = QLabel("description")
        mid_layout.addWidget(description_label)
        mid_layout.addStretch()

        right_layout = QVBoxLayout()
        right_widget = QWidget()
        right_widget.setLayout(right_layout)
        image_label = QLabel(self)
        right_layout.addWidget(image_label)
        right_layout.addStretch()

        infos = QHBoxLayout()
        infos.addWidget(board_table, stretch=1)
        infos.addWidget(mid_widget, stretch=3)
        infos.addWidget(right_widget, stretch=1)

        dialog.layout.addLayout(infos)
        dialog.layout.addWidget(dialog_buttonBox)

        show_board_info(0)

        if dialog.exec():
            return dialog.selected

    def check_status(self):
        self.config_checked = self.clean_config(self.config)
        config_name = self.config.get("name")
        self.button_save.setEnabled(True)
        self.button_save_as.setEnabled(True)

        if self.config_original != self.clean_config(self.config):
            self.info_saved.setChecked(False)
            self.button_save.setStyleSheet("background-color: red;")
            self.button_save_as.setStyleSheet("background-color: red;")
            self.info_generated.setChecked(False)
            self.button_generate.setStyleSheet("background-color: red;")
            self.button_generate.setEnabled(False)
            self.button_compile.setEnabled(False)
            self.button_flash.setEnabled(False)
        else:
            self.info_saved.setChecked(True)
            self.button_save.setStyleSheet("background-color: green;")
            self.button_save_as.setStyleSheet("background-color: green;")
            self.button_generate.setEnabled(True)

            # checking generated config
            if os.path.isfile(f"Output/{config_name}/.config.json"):
                ret = os.system(f"diff {self.config_file} Output/{config_name}/.config.json >/dev/null")
            else:
                ret = 1
            if ret == 0:
                self.info_generated.setChecked(True)
                self.button_generate.setStyleSheet("background-color: green;")
                self.button_compile.setEnabled(True)
            else:
                self.info_generated.setChecked(False)
                self.button_generate.setStyleSheet("background-color: red;")
                self.button_compile.setEnabled(False)

        # checking gateware
        hash_compiled = ""
        hash_compiled_file = f"Output/{config_name}/Gateware/hash_compiled.txt"
        if os.path.isfile(hash_compiled_file):
            hash_compiled = open(hash_compiled_file, "r").read()
        if hash_compiled == self.gateware_hash:
            self.info_compiled.setChecked(True)
            self.button_compile.setStyleSheet("background-color: green;")
            self.button_flash.setEnabled(True)
        else:
            self.info_compiled.setChecked(False)
            self.button_compile.setStyleSheet("background-color: red;")
            self.button_flash.setEnabled(False)

        hash_flashed = ""
        hash_flashed_file = f"Output/{config_name}/Gateware/hash_flashed.txt"
        if os.path.isfile(hash_flashed_file):
            hash_flashed = open(hash_flashed_file, "r").read()
        if hash_flashed == self.gateware_hash:
            self.info_flashed.setChecked(True)
            self.button_flash.setStyleSheet("background-color: green;")
        else:
            self.info_flashed.setChecked(False)
            self.button_flash.setStyleSheet("background-color: red;")

    def runTimer(self):
        for tab in self.tabs:
            self.tabs[tab].timer()

        if self.request_generate > 1:
            self.request_generate -= 1
        elif self.request_generate == 1:
            self.generate_cb(preview=True)
            self.request_generate = 0

        if self.request_load_tree > 1:
            self.request_load_tree -= 1
        elif self.request_load_tree == 1:
            self.load_tree()
            self.request_load_tree = 0

        if self.request_pin_table_load > 1:
            self.request_pin_table_load -= 1
        elif self.request_pin_table_load == 1:
            self.tabs["Pins"].update()
            self.tabs["Board"].update()
            self.request_pin_table_load = 0

        if self.request_sig_table_load > 1:
            self.request_sig_table_load -= 1
        elif self.request_sig_table_load == 1:
            self.tabs["Signals"].update()
            self.request_sig_table_load = 0

        if self.config_checked != self.clean_config(self.config):
            self.check_status()

        if self.compile_sub is not None:
            widget = self.tabs["Gateware"].gateware["Compile-Output"]
            config_name = self.config.get("name")
            logdata = open(f"Output/{config_name}/Gateware/compile.log", "r").read()
            widget.clear()
            duration = time.time() - self.compile_start

            if self.compile_sub.poll() is not None:
                widget.insertPlainText(logdata)
                widget.verticalScrollBar().setValue(widget.verticalScrollBar().maximum())
                self.compile_sub = None
                self.check_status()
                self.info_widget.setText(f"compile...done in {duration:0.1f}s")
            else:
                widget.insertPlainText(logdata)
                widget.verticalScrollBar().setValue(widget.verticalScrollBar().maximum())
                self.button_save.setEnabled(False)
                self.button_save_as.setEnabled(False)
                self.button_generate.setEnabled(False)
                self.button_compile.setEnabled(False)
                self.button_flash.setEnabled(False)
                self.info_widget.setText(f"compile...({duration:0.1f}s)")

        if self.flash_sub is not None:
            widget = self.tabs["Gateware"].gateware["Flash-Output"]
            config_name = self.config.get("name")
            logdata = open(f"Output/{config_name}/Gateware/flash.log", "r").read()
            widget.clear()
            duration = time.time() - self.flash_start

            if self.flash_sub.poll() is not None:
                widget.insertPlainText(logdata)
                widget.verticalScrollBar().setValue(widget.verticalScrollBar().maximum())
                self.flash_sub = None
                self.check_status()
                self.info_widget.setText(f"flash...done in {duration:0.1f}s")
            else:
                widget.insertPlainText(logdata)
                widget.verticalScrollBar().setValue(widget.verticalScrollBar().maximum())
                self.button_save.setEnabled(False)
                self.button_save_as.setEnabled(False)
                self.button_generate.setEnabled(False)
                self.button_flash.setEnabled(False)
                self.info_widget.setText(f"flash...({duration:0.1f}s)")

    def itemChanged(self, item):
        pass

    def json_load(self):
        # loading json config
        if self.config_file:
            print(f"loading config: {self.config_file}")
            configJsonStr = open(self.config_file, "r").read()
            if self.config_file.endswith(".yml"):
                self.config = yaml.load(configJsonStr)
            else:
                self.config = json.loads(configJsonStr)

        if "plugins" not in self.config:
            self.config["plugins"] = []

        # loading board config
        boardcfg = self.config.get("boardcfg")
        self.boardcfg_path = None
        if boardcfg:
            board_file = self.get_boardpath(boardcfg)
            self.boardcfg_path = os.path.dirname(board_file)
            self.board = {}
            print(f"loading board: {board_file}")
            boardJsonStr = open(board_file, "r").read()
            self.board = json.loads(boardJsonStr)

        self.config_load()

    def closeEvent(self, event):
        if self.config_original != self.clean_config(self.config):
            self.save_config_as()

    def setup_merge(self, setup, defaults):
        for key, value in defaults.items():
            if key not in setup:
                setup[key] = copy.deepcopy(value)
            elif isinstance(value, dict):
                self.setup_merge(setup[key], value)

    def get_path(self, path):
        if os.path.exists(path):
            return path
        elif os.path.exists(f"{riocore_path}/{path}"):
            return f"{riocore_path}/{path}"
        elif os.path.exists(f"{riocore_path}/{path}"):
            return f"{riocore_path}/{path}"
        print(f"can not find path: {path}")
        exit(1)

    def get_boardpath(self, board):
        pathes = [
            f"{board}.json",
            f"{riocore_path}/boards/{board}.json",
            f"{riocore_path}/boards/{board}/board.json",
        ]
        for path in pathes:
            if os.path.exists(path):
                return path
        print(f"can not find board: {board}")
        exit(1)

    def testgui(self):
        print("starting testgui..", f"{os.path.dirname(__file__)}/rio-test")
        filename = f"{self.config_file}.test-gui-temp.json"
        self.save_config(filename)
        testgui_path = f"{os.path.dirname(__file__)}/rio-test"
        os.system(f"({testgui_path} {filename} ; rm {filename}) &")

    def add_plugin(self, pin_id, slot_name=None):
        boardcfg = self.config.get("boardcfg")
        toolchain = self.board.get("toolchain")
        family = self.board.get("family")
        plugin_needs = {}
        plugin_list = self.plugins.list()
        plugin_infos = {}
        for plugin in plugin_list:
            plugins = riocore.Plugins()
            plugins.load_plugins({"plugins": [{"type": plugin["name"]}]})

            limit_boards = plugins.plugin_instances[0].LIMITATIONS.get("boards")
            if limit_boards and boardcfg not in limit_boards:
                continue

            limit_toolchains = plugins.plugin_instances[0].LIMITATIONS.get("toolchains")
            if limit_toolchains and toolchain not in limit_toolchains:
                continue

            limit_family = plugins.plugin_instances[0].LIMITATIONS.get("family")
            if limit_family and family not in limit_family:
                continue

            plugin_needs[plugin["name"]] = {
                "inputs": 0,
                "outputs": 0,
                "inouts": 0,
                "opt_inputs": 0,
                "opt_outputs": 0,
                "opt_inouts": 0,
            }
            for pin_name, pin_defaults in plugins.plugin_instances[0].PINDEFAULTS.items():
                direction = pin_defaults["direction"]
                key = f"{direction}s"
                if pin_defaults.get("optional", False):
                    key = f"opt_{key}"
                plugin_needs[plugin["name"]][key] += 1
            plugin_infos[plugin["name"]] = {
                "description": plugins.plugin_instances[0].DESCRIPTION,
                "info": plugins.plugin_instances[0].INFO,
                "pins": plugins.plugin_instances[0].PINDEFAULTS,
                "signals": plugins.plugin_instances[0].SIGNALS,
            }

        possible_plugins = []
        if slot_name:
            # filter possible plugins if slot is set
            for slot in self.slots:
                if slot_name == slot["name"]:
                    compatible = slot.get("compatible")
                    if compatible:
                        possible_plugins = compatible
                    else:
                        default = slot.get("default")
                        if default:
                            possible_plugins.append(default)
                        slot_has = {
                            "inputs": 0,
                            "outputs": 0,
                            "inouts": 0,
                            "alls": 0,
                        }
                        for _pin_id, pin in slot["pins"].items():
                            if isinstance(pin, dict):
                                direction = pin.get("direction") or "all"
                                slot_has[f"{direction}s"] += 1

                        for pname, plugin_data in plugin_needs.items():
                            match = True
                            for key in ("inputs", "outputs", "inouts"):
                                if not (slot_has[key] >= plugin_data[key] and slot_has[key] <= plugin_data[key] + plugin_data[f"opt_{key}"]):
                                    match = False
                            if match and pname and pname not in possible_plugins:
                                possible_plugins.append(pname)
                        for pname, plugin_data in plugin_needs.items():
                            match = True
                            for key in ("inputs", "outputs", "inouts"):
                                if slot_has[key] + slot_has["alls"] < plugin_data[key]:
                                    match = False
                            if match and pname and pname not in possible_plugins:
                                possible_plugins.append(pname)
                    break
        else:
            for pname, plugin_data in plugin_needs.items():
                possible_plugins.append(pname)

        dialog = QDialog()
        dialog.setWindowTitle("select plugin")
        dialog.setStyleSheet(STYLESHEET)

        dialog.layout = QVBoxLayout()
        dialog_buttonBox = QDialogButtonBox(QDialogButtonBox.Ok)
        dialog_buttonBox.accepted.connect(dialog.accept)
        dialog.setLayout(dialog.layout)

        def show_plugin_info(idx):
            plugin_name = possible_plugins[idx]
            plugin_path = f"{riocore_path}/plugins/{plugin_name}"
            image_path = f"{plugin_path}/image.png"
            if os.path.isfile(image_path):
                pixmap = QPixmap(image_path)
                image_label.setPixmap(pixmap)
            else:
                image_label.clear()
            name_label.setText(plugin_name.replace("_", "-").title())
            info_label.setText(plugin_infos[plugin_name]["info"])
            description = plugin_infos[plugin_name]["description"] or "---"
            description += "\n\nPins:\n"
            for pin_name, pin_info in plugin_infos[plugin_name]["pins"].items():
                optional = pin_info.get("optional")
                if optional is True:
                    description += f"  {pin_name}: {pin_info['direction']} (optional)\n"
                else:
                    description += f"  {pin_name}: {pin_info['direction']}\n"
            description += "\nSignals:\n"
            for signal_name, signal_info in plugin_infos[plugin_name]["signals"].items():
                description += f"  {signal_name}: {signal_info['direction']}\n"

            description_label.setText(description)
            dialog.selected = plugin_name

        plugin_table = QTableWidget()
        plugin_table.setColumnCount(1)
        plugin_table.setHorizontalHeaderItem(0, QTableWidgetItem("Plugins"))
        plugin_table.setRowCount(len(possible_plugins))
        for row, plugin_name in enumerate(possible_plugins):
            pitem = QTableWidgetItem(plugin_name)
            plugin_table.setItem(row, 0, pitem)
        plugin_table.setFixedWidth(200)
        plugin_table.cellClicked.connect(show_plugin_info)
        plugin_table.currentCellChanged.connect(show_plugin_info)

        mid_layout = QVBoxLayout()
        mid_widget = QWidget()
        mid_widget.setFixedWidth(400)
        mid_widget.setLayout(mid_layout)
        name_label = QLabel("name")
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
        image_label = QLabel(self)
        right_layout.addWidget(image_label)
        right_layout.addStretch()

        infos = QHBoxLayout()
        infos.addWidget(plugin_table, stretch=1)
        infos.addWidget(mid_widget, stretch=3)
        infos.addWidget(right_widget, stretch=1)

        dialog.layout.addLayout(infos)
        dialog.layout.addWidget(dialog_buttonBox)

        show_plugin_info(0)

        if dialog.exec():
            plugin_id = len(self.config["plugins"])
            self.config["plugins"].append(
                {
                    "type": dialog.selected,
                    "pins": {},
                }
            )

            plugin_config = self.config["plugins"][plugin_id]
            plugin_instance = self.plugins.load_plugin(plugin_id, plugin_config, self.config)

            if "pins" not in plugin_config:
                plugin_config["pins"] = {}

            for pin_name, pin_defaults in plugin_instance.PINDEFAULTS.items():
                if pin_name not in plugin_config["pins"]:
                    plugin_config["pins"][pin_name] = {}

            if plugin_instance:
                # auto select pins if slot is set
                if slot_name:
                    slotpins = {
                        "input": [],
                        "output": [],
                        "inout": [],
                        "all": [],
                    }
                    for spin_name, spin in slot.get("pins", {}).items():
                        direction = spin.get("direction") or "all"
                        if self.get_plugin_by_pin(spin["pin"]) == (None, None):
                            if direction:
                                slotpins[direction].append(spin_name)

                    # map single pin plugin to pin_id
                    num_mandatory = 0
                    for pin_name, pin_defaults in plugin_instance.PINDEFAULTS.items():
                        optional = pin_defaults.get("optional")
                        if optional is True:
                            continue
                        num_mandatory += 1

                    if num_mandatory == 1:
                        for pin_name, pin_defaults in plugin_instance.PINDEFAULTS.items():
                            optional = pin_defaults.get("optional")
                            if optional is True:
                                continue
                            direction = pin_defaults.get("direction") or "all"
                            pinconfig = {"pin": f"{slot_name}:{pin_id}"}
                            if direction in slotpins and pin_id in slotpins[direction]:
                                slotpins[direction].remove(pin_id)
                            self.config["plugins"][plugin_id]["pins"][pin_name] = pinconfig
                    else:
                        # first mandatory pins
                        for pin_name, pin_defaults in plugin_instance.PINDEFAULTS.items():
                            optional = pin_defaults.get("optional")
                            if optional is True:
                                continue
                            direction = pin_defaults.get("direction") or "all"
                            pinconfig = {"pin": ""}
                            # find matching pins by name
                            found = False
                            for spin in slotpins[direction]:
                                if pin_name.lower() == spin.lower():
                                    pinconfig = {"pin": f"{slot_name}:{spin}"}
                                    slotpins[direction].remove(spin)
                                    found = True
                                    break
                            for spin in slotpins["all"]:
                                if pin_name.lower() == spin.lower():
                                    pinconfig = {"pin": f"{slot_name}:{spin}"}
                                    slotpins["all"].remove(spin)
                                    found = True
                                    break
                            if not found:
                                # find matching pins by direction
                                for spin in slotpins[direction]:
                                    pinconfig = {"pin": f"{slot_name}:{spin}"}
                                    slotpins[direction].remove(spin)
                                    found = True
                                    break
                                for spin in slotpins["all"]:
                                    pinconfig = {"pin": f"{slot_name}:{spin}"}
                                    slotpins["all"].remove(spin)
                                    found = True
                                    break
                            self.config["plugins"][plugin_id]["pins"][pin_name] = pinconfig

                        # then optional pins
                        for pin_name, pin_defaults in plugin_instance.PINDEFAULTS.items():
                            optional = pin_defaults.get("optional", False)
                            if optional is False:
                                continue
                            direction = pin_defaults.get("direction") or "all"
                            pinconfig = {"pin": None}
                            # find matching pins by name
                            found = False
                            for spin in slotpins[direction]:
                                if pin_name.lower() == spin.lower():
                                    pinconfig = {"pin": f"{slot_name}:{spin}"}
                                    slotpins[direction].remove(spin)
                                    found = True
                                    break
                            if not found:
                                # find matching pins by direction
                                for spin in slotpins[direction]:
                                    pinconfig = {"pin": f"{slot_name}:{spin}"}
                                    slotpins[direction].remove(spin)
                                    found = True
                                    break
                            self.config["plugins"][plugin_id]["pins"][pin_name] = pinconfig

                self.tree_add_plugin(self.tree_plugins, plugin_instance, expand=True)
                self.display()

                self.edit_plugin(plugin_instance, None, is_new=True)

            return dialog.selected

    def get_plugin_by_pin(self, pinsearch):
        for plugin_instance in self.plugins.plugin_instances:
            for pin_name, pin_defaults in plugin_instance.PINDEFAULTS.items():
                pin_setup = plugin_instance.plugin_setup.get("pins", {}).get(pin_name, {})
                if not pin_setup and pin_defaults.get("optional") is True:
                    continue
                if "pin" not in pin_setup and pin_defaults.get("optional") is True:
                    continue
                pin_str = pin_setup.get("pin", "")
                if pinsearch == pin_str:
                    return (plugin_instance, pin_name)

                pin_real = pin_str
                if pin_str in self.pinmapping:
                    pin_real = self.pinmapping[pin_str]
                if pinsearch == pin_real:
                    return (plugin_instance, pin_name)

        return (None, None)

    def get_module_by_slot(self, slot_name):
        if slot_name in self.modules:
            return self.modules[slot_name]["name"]
        return

    def config_load(self):
        self.info_widget.setText(self.config_file)

        slot_pinmapping = {}
        self.slots = self.board.get("slots", []) + self.config.get("slots", [])
        for slot in self.slots:
            slot_name = slot["name"]
            for pin_id, pin in slot["pins"].items():
                if isinstance(pin, dict):
                    pin = pin["pin"]
                pin_name = f"{slot_name}:{pin_id}"
                slot_pinmapping[pin] = pin_name

        # loading slot/module configs
        self.modules = {}
        for module in self.config.get("modules", []):
            slot_name = module.get("slot")
            module_name = module.get("module")
            module_setup = module.get("setup", {})
            module_path = self.get_path(f"modules/{module_name}.json")
            moduleJsonStr = open(module_path, "r").read()
            module_defaults = json.loads(moduleJsonStr)

            mplugins = riocore.Plugins()
            for plugin_id, plugin_config in enumerate(module_defaults.get("plugins", [])):
                plugin_name = plugin_config.get("name")
                if plugin_name not in module_setup:
                    module_setup[plugin_name] = {}
                self.setup_merge(module_setup[plugin_name], plugin_config)
                if "pins" in module_setup[plugin_name]:
                    for pin in module_setup[plugin_name]["pins"]:
                        if "pin" in module_setup[plugin_name]["pins"][pin]:
                            module_setup[plugin_name]["pins"][pin]["pin_mapped"] = module_setup[plugin_name]["pins"][pin]["pin"]
                            del module_setup[plugin_name]["pins"][pin]["pin"]

                mplugins.load_plugin(plugin_id, module_setup[plugin_name], self.config)

            self.modules[slot_name] = {
                "name": module_name,
                "defaults": module_defaults,
                "setup": module_setup,
                "instances": mplugins.plugin_instances,
            }

        # loading plugins
        self.plugins = riocore.Plugins()
        for plugin_id, plugin_config in enumerate(self.config.get("plugins", [])):
            self.plugins.load_plugin(plugin_id, plugin_config, self.config)

        self.items = {}
        self.pinlist = []
        self.pinmapping = {}
        self.pinmapping_rev = {}
        self.expansion_pins = []
        for plugin_instance in self.plugins.plugin_instances:
            if plugin_instance.TYPE == "expansion":
                for pin in plugin_instance.expansion_outputs():
                    self.expansion_pins.append(pin)
                    if pin not in self.pinlist:
                        self.pinlist.append(pin)
                for pin in plugin_instance.expansion_inputs():
                    self.expansion_pins.append(pin)
                    if pin not in self.pinlist:
                        self.pinlist.append(pin)

            for pin_name, pin_defaults in plugin_instance.PINDEFAULTS.items():
                if "pins" not in plugin_instance.plugin_setup:
                    continue
                if pin_name not in plugin_instance.plugin_setup["pins"]:
                    plugin_instance.plugin_setup["pins"][pin_name] = {}
                pin_setup = plugin_instance.plugin_setup["pins"][pin_name]
                if not pin_setup and pin_defaults.get("optional") is True:
                    continue
                if "pin" not in pin_setup and pin_defaults.get("optional") is True:
                    continue
                pin = pin_setup.get("pin")
                if pin not in self.pinlist:
                    self.pinlist.append(pin)
        for slot in self.slots:
            slot_name = slot.get("name")
            slot_pins = slot.get("pins", {})
            for pin_name, pin in slot_pins.items():
                if isinstance(pin, dict):
                    pin = pin["pin"]
                pin_id = f"{slot_name}:{pin_name}"
                if pin not in self.pinlist:
                    self.pinlist.append(pin)
                self.pinmapping[pin_id] = pin
                self.pinmapping_rev[pin] = pin_id
                if pin_id not in self.pinlist:
                    self.pinlist.append(pin_id)

        def sort_key(value):
            if not value:
                return ""
            numbers = re.findall(r"\d+", value)
            for number in numbers:
                value = value.replace(number, f"{int(number):09d}")
            return value

        def load_pins(board):
            # try to load list of pins from chipdb files
            family = board.get("family")
            fpga_type = board.get("type")
            package = board.get("package")
            check_name = family.lower().replace(" ", "_")
            check_path = f"riocore/chipdata/{check_name}.json"
            if os.path.isfile(check_path):
                chipJsonStr = open(check_path, "r").read()
                chipData = json.loads(chipJsonStr)
                for fpga_id in [fpga_type, fpga_type.replace("up", "")]:
                    if fpga_id in chipData:
                        if package in chipData[fpga_id]:
                            for pin_name in chipData[fpga_id][package]:
                                if pin_name not in self.pinlist:
                                    self.pinlist.append(pin_name)
                        break

        load_pins(self.board)
        self.pinlist.sort(key=sort_key)

        boards_path = self.get_path("boards/")
        modules_path = self.get_path("modules/")

        self.interfaces = []
        for path in sorted(glob.glob(f"{riocore_path}/interfaces/*")):
            self.interfaces.append(path.split("/")[-1])
        self.boards = []
        for path in sorted(glob.glob(f"{boards_path}/*/board.json")):
            self.boards.append(path.split("/")[-2].split(".")[0])
        for path in sorted(glob.glob(f"{boards_path}/*.json")):
            self.boards.append(path.split("/")[-1].split(".")[0])
        self.module_names = []
        for path in sorted(glob.glob(f"{modules_path}/*.json")):
            self.module_names.append(path.split("/")[-1].split(".")[0])
        self.slotnames = []
        for slot in self.slots:
            slot_name = slot.get("name")
            if slot_name:
                self.slotnames.append(slot_name)

        self.tabs["Board"].update()
        self.load_tree()
        self.tabs["Pins"].update()
        self.tabs["Signals"].update()
        self.display()

    def display(self):
        try:
            self.request_generate = 2
            self.request_pin_table_load = 2
            self.request_sig_table_load = 2
            self.tabs["Overview"].update()
            self.tabs["Json"].update()
            self.info_widget.setText(self.config_file)
        except Exception as error:
            print(f"ERROR: {error}")
            self.info_widget.setText(f"ERROR: {error}")

    def open_pyvcp(self):
        try:
            if os.system("pidof linuxcncsvr") == 0:
                print("ERROR: linuxcnc is running")
                self.info_widget.setText("ERROR: linuxcnc is running")
            else:
                self.generate_cb(preview=True)
                if "rio-gui.xml" in self.linuxcnc:
                    xml_data = self.linuxcnc["rio-gui.xml"].toPlainText()
                    if xml_data:
                        tmp_file = ".tmp_rio-gui.xml"
                        os.system('ps fax | grep "pyvcp .tmp_rio-gui.xml" | grep -v grep | cut -d" " -f1 | xargs -r -l kill -4')
                        os.system("halcmd stop")
                        open(tmp_file, "w").write(xml_data)
                        os.system(f"(pyvcp '{tmp_file}' ; rm -f '{tmp_file}') &")
        except Exception as error:
            print(f"ERROR: {error}")
            self.info_widget.setText(f"ERROR: {error}")

    def struct_clean(self, data):
        # removing empty lists and dicts
        for key in list(data):
            if isinstance(data[key], list):
                for pn, part in enumerate(data[key]):
                    if isinstance(part, dict):
                        if not part:
                            print("DEL1", key, pn, data[key][pn])
                            del data[key][pn]
                        else:
                            self.struct_clean(data[key][pn])
                if not data[key]:
                    del data[key]
            elif isinstance(data[key], dict):
                self.struct_clean(data[key])
                if not data[key]:
                    del data[key]
            elif data[key] is None:
                del data[key]

    def clean_config(self, config_unclean):
        config = copy.deepcopy(config_unclean)
        # cleanup
        for module in config.get("modules", []):
            for name, setup in module.get("setup", {}).items():
                for pin, pin_setup in setup.get("pins", {}).items():
                    if "pin_mapped" in pin_setup:
                        del pin_setup["pin_mapped"]
        for plugin in config.get("plugins", []):
            for name, plugin_config in plugin.get("config", {}).items():
                if "instance" in plugin_config:
                    del plugin_config["instance"]
        self.struct_clean(config)
        return config

    def edit_item(self, obj, key, var_setup=None, cb=None):
        if var_setup is None:
            var_setup = {}
        # if key not in obj and "default" in var_setup:
        #    obj[key] = var_setup["default"]

        if var_setup["type"] == "select":
            return edit_combobox(self, obj, key, var_setup.get("options", []), cb=cb, default=var_setup.get("default"))
        elif var_setup["type"] == int:
            return edit_int(self, obj, key, vmin=var_setup.get("min"), vmax=var_setup.get("max"), cb=cb, default=var_setup.get("default"))
        elif var_setup["type"] == float:
            return edit_float(self, obj, key, vmin=var_setup.get("min"), vmax=var_setup.get("max"), cb=cb, default=var_setup.get("default"), decimals=var_setup.get("decimals"))
        elif var_setup["type"] == bool:
            return edit_bool(self, obj, key, cb=cb, default=var_setup.get("default"))
        return edit_text(self, obj, key, cb=cb, default=var_setup.get("default"))

    def del_module(self, slot_name):
        for mn, module_data in enumerate(self.config.get("modules", [])):
            if slot_name == module_data.get("slot"):
                self.config["modules"].pop(mn)
                break
        self.config_load()
        self.display()
        self.tree_expand("/Modules/")

    def load_tree(self, expand=None):
        while self.model.rowCount() > 0:
            self.model.removeRow(0)

        for key, var_setup in {
            "name": {"type": str},
            "description": {"type": str},
            "boardcfg": {"type": "select", "options": self.boards},
            "protocol": {"type": "select", "options": self.interfaces, "default": "SPI"},
        }.items():
            aitem = MyStandardItem()
            self.model.appendRow(
                [
                    MyStandardItem(key.title()),
                    aitem,
                ]
            )
            self.treeview.setIndexWidget(aitem.index(), self.edit_item(self.config, key, var_setup))

        # LinuxCNC
        bitem = MyStandardItem()
        self.model.appendRow(
            [
                MyStandardItem("LinuxCNC", help_text="LinuxCNC specific configurations"),
                bitem,
            ]
        )
        tree_lcnc = self.model.item(self.model.rowCount() - 1)
        if "linuxcnc" not in self.config:
            self.config["linuxcnc"] = {}

        for key, var_setup in {
            "num_axis": {"type": int, "min": 0, "max": 9, "default": 3},
            "machinetype": {"type": "select", "options": ["mill", "lathe", "corexy", "ldelta", "rdelta", "scara", "puma", "melfa"]},
            "toolchange": {"type": "select", "options": ["manual", "auto"], "default": "manual"},
            "gui": {"type": "select", "options": ["axis", "qtdragon", "tklinuxcnc", "touchy", "probe_basic"], "default": "axis"},
            "embed_vismach": {"type": "select", "options": ["", "fanuc_200f"], "default": ""},
        }.items():
            aitem = MyStandardItem()
            tree_lcnc.appendRow(
                [
                    MyStandardItem(key.title()),
                    aitem,
                ]
            )
            self.treeview.setIndexWidget(aitem.index(), self.edit_item(self.config["linuxcnc"], key, var_setup))

        # linuxcnc addon's
        bitem = MyStandardItem()
        tree_lcnc.appendRow(
            [
                MyStandardItem("AddOn's", help_text="LinuxCNC generator addons"),
                bitem,
            ]
        )
        tree_lcncaddons = tree_lcnc.child(tree_lcnc.rowCount() - 1)
        for addon_name, addon in self.addons.items():
            if hasattr(addon, "load_tree"):
                addon.load_tree(self, tree_lcncaddons)

        # rio-functions
        bitem = MyStandardItem()
        tree_lcnc.appendRow(
            [
                MyStandardItem("RIO-Functions", help_text="default values for the RIO-Functions"),
                bitem,
            ]
        )
        tree_lcncriof = tree_lcnc.child(tree_lcnc.rowCount() - 1)
        if "rio_functions" not in self.config["linuxcnc"]:
            self.config["linuxcnc"]["rio_functions"] = {}
        riof_config = self.config["linuxcnc"]["rio_functions"]

        riof_data = halpins.RIO_FUNCTION_DEFAULTS
        for function, function_data in riof_data.items():
            if function not in riof_config:
                riof_config[function] = {}

            aitem = MyStandardItem()
            tree_lcncriof.appendRow(
                [
                    MyStandardItem(function.title()),
                    MyStandardItem(""),
                ]
            )
            lcncfunc_view = tree_lcncriof.child(tree_lcncriof.rowCount() - 1)
            for section, section_data in function_data.items():
                if section not in riof_config[function]:
                    riof_config[function][section] = {}
                section_config = riof_config[function][section]
                aitem = MyStandardItem()
                lcncfunc_view.appendRow(
                    [
                        MyStandardItem(section.title()),
                        MyStandardItem(""),
                    ]
                )
                lcncsec_view = lcncfunc_view.child(lcncfunc_view.rowCount() - 1)
                for key, var_setup in section_data.items():
                    key_title = key.title()
                    aitem = MyStandardItem()
                    lcncsec_view.appendRow(
                        [
                            MyStandardItem(key_title, help_text=var_setup.get("help", key)),
                            aitem,
                        ]
                    )
                    self.treeview.setIndexWidget(aitem.index(), self.edit_item(section_config, key, var_setup))

        # linuxcnc-ini
        bitem = MyStandardItem()
        tree_lcnc.appendRow(
            [
                MyStandardItem("INI-Defaults", help_text="LinuxCNC INI-Defaults"),
                bitem,
            ]
        )
        tree_lcncini = tree_lcnc.child(tree_lcnc.rowCount() - 1)
        if "ini" not in self.config["linuxcnc"]:
            self.config["linuxcnc"]["ini"] = {}
        ini_config = self.config["linuxcnc"]["ini"]

        ini_data = riocore.generator.LinuxCNC.LinuxCNC.ini_defaults(self.config)
        for section, section_data in ini_data.items():
            if section not in ini_config:
                ini_config[section] = {}
            section_config = ini_config[section]

            aitem = MyStandardItem()
            tree_lcncini.appendRow(
                [
                    MyStandardItem(section),
                    MyStandardItem(""),
                ]
            )
            lcncsec_view = tree_lcncini.child(tree_lcncini.rowCount() - 1)
            for key, value in section_data.items():
                if value is not None and not isinstance(value, list):
                    var_setup = {"type": type(value), "default": value}
                    if section == "DISPLAY" and key == "POSITION_OFFSET":
                        var_setup["type"] = "select"
                        var_setup["options"] = ["RELATIVE", "MACHINE"]
                    if section == "DISPLAY" and key == "POSITION_FEEDBACK":
                        var_setup["type"] = "select"
                        var_setup["options"] = ["COMMANDED", "ACTUAL"]
                    if section == "HAL" and key == "TWOPASS":
                        var_setup["type"] = "select"
                        var_setup["options"] = ["ON", "OFF"]
                    if section == "DISPLAY" and key == "PYVCP_POSITION":
                        var_setup["type"] = "select"
                        var_setup["options"] = ["RIGHT", "BOTTOM"]

                    if section in halpins.INI_HELPTEXT and key in halpins.INI_HELPTEXT[section]:
                        var_setup["tooltip"] = halpins.INI_HELPTEXT[section][key]

                    key_title = key
                    if "|" in key:
                        key_title = f"{key.split('|')[0]} ({key.split('|')[1]})"
                    aitem = MyStandardItem()
                    lcncsec_view.appendRow(
                        [
                            MyStandardItem(key_title, help_text=var_setup.get("tooltip")),
                            aitem,
                        ]
                    )
                    self.treeview.setIndexWidget(aitem.index(), self.edit_item(section_config, key, var_setup))

        # modules
        free_slots = False
        for slot in self.slots:
            slot_name = slot["name"]
            if slot_name not in self.modules:
                free_slots = True
                break

        bitem = MyStandardItem()
        self.model.appendRow(
            [
                MyStandardItem("Modules", help_text="Module-Configuration"),
                bitem,
            ]
        )
        tree_modules = self.model.item(self.model.rowCount() - 1)

        if free_slots:
            button = QPushButton("add module")
            button.clicked.connect(self.add_module)
            button.setMaximumSize(button.sizeHint())
            self.treeview.setIndexWidget(bitem.index(), button)

        for module_data in self.config.get("modules", []):
            slot_name = module_data.get("slot")
            module_name = module_data.get("module")
            title = slot_name
            if module_name:
                title = f"{module_name} ({title})"
            aitem = MyStandardItem()
            tree_modules.appendRow(
                [
                    MyStandardItem(title),
                    aitem,
                ]
            )
            module_view = tree_modules.child(tree_modules.rowCount() - 1)

            button = QPushButton("delete")
            cb = partial(self.del_module, slot_name)
            button.clicked.connect(cb)
            button.setMaximumSize(button.sizeHint())
            self.treeview.setIndexWidget(aitem.index(), button)

            for key, var_setup in {
                "module": {"type": "select", "options": self.module_names},
                "slot": {"type": "select", "options": self.slotnames},
            }.items():
                aitem = MyStandardItem()
                module_view.appendRow(
                    [
                        MyStandardItem(key.title()),
                        aitem,
                    ]
                )
                self.treeview.setIndexWidget(aitem.index(), self.edit_item(module_data, key, var_setup, cb=self.slot_change))

            module_plugins_view = MyStandardItem("Plugins")
            module_view.appendRow(module_plugins_view)

            for plugin_instance in self.modules[slot_name]["instances"]:
                self.tree_add_plugin(module_plugins_view, plugin_instance, nopins=True, expand=False)

        bitem = MyStandardItem()
        self.model.appendRow(
            [
                MyStandardItem("Plugins"),
                bitem,
            ]
        )
        self.tree_plugins = self.model.item(self.model.rowCount() - 1)

        buttons_layout = QHBoxLayout()
        buttons_layout.setContentsMargins(0, 0, 0, 0)
        buttons_widget = QWidget()
        buttons_widget.setLayout(buttons_layout)

        button = QPushButton("add plugin")
        button.clicked.connect(self.add_plugin)
        button.setMaximumSize(button.sizeHint())
        buttons_layout.addWidget(button)

        buttons_layout.addStretch()
        self.treeview.setIndexWidget(bitem.index(), buttons_widget)

        for plugin_instance in self.plugins.plugin_instances:
            self.tree_add_plugin(self.tree_plugins, plugin_instance)

        self.treeview.header().resizeSection(0, 300)
        self.treeview.header().resizeSection(1, 200)

        if expand:
            self.tree_expand(expand)
        else:
            self.tree_expand("/Plugins/")

    def tree_expand(self, tpath):
        def iter_childs(entry, prefix=""):
            row = 0
            item = self.model.itemData(entry.child(row, 0))
            while item:
                row += 1
                child = entry.child(row, 0)
                item = self.model.itemData(child)
                if item:
                    title = item[0]
                    if tpath.startswith(f"{prefix}/{title}"):
                        self.treeview.expand(child)
                    iter_childs(child, prefix=f"{prefix}/{title}")

        row = 0
        item = self.model.itemData(self.model.index(row, 0))
        while item:
            row += 1
            child = self.model.index(row, 0)
            item = self.model.itemData(child)
            if item:
                title = item[0]
                if tpath.startswith(f"/{title}"):
                    self.treeview.expand(child)
                iter_childs(self.model.index(row, 0), prefix=f"/{title}")

    def slot_change(self, widget):
        self.config_load()

    def add_modifier(self, parent, pin_setup):
        if "modifier" not in pin_setup:
            pin_setup["modifier"] = []
        modifier_id = len(pin_setup.get("modifier", []))
        pin_setup["modifier"].append({"type": "invert"})
        modifier = pin_setup["modifier"][-1]
        self.tree_add_modifier(parent, pin_setup, modifier_id, modifier)
        self.display()

    def add_module(self, widget, slot_name=None, module_name=None, slot_select=True):
        last_error = None
        while True:
            ret = self.select_module(last_error=last_error, set_slot=slot_name, set_module=module_name, slot_select=slot_select)
            if not ret:
                return
            slot_name, module_name = ret
            if not module_name or not slot_name:
                return

            module_path = self.get_path(f"modules/{module_name}.json")
            moduleJsonStr = open(module_path, "r").read()
            module_defaults = json.loads(moduleJsonStr)

            slot_setup = {}
            for slot in self.slots:
                if slot_name == slot["name"]:
                    slot_setup = slot
            slot_pins = slot_setup.get("pins", {})

            check = True
            for plugin in module_defaults.get("plugins"):
                for pin_name, pin_config in plugin.get("pins", {}).items():
                    pin_location = pin_config.get("pin")
                    # print(pin_location, slot_pins)
                    if pin_location not in slot_pins:
                        check = False

            if check is True:
                break
            else:
                last_error = "ERROR: module/slot is not compatible"
                print(last_error)

        if "modules" not in self.config:
            self.config["modules"] = []

        module_setup = {}
        self.config["modules"].append(
            {
                "slot": slot_name,
                "module": module_name,
                "setup": module_setup,
            }
        )

        mplugins = riocore.Plugins()
        for plugin_id, plugin_config in enumerate(module_defaults.get("plugins", [])):
            plugin_name = plugin_config.get("name")
            if plugin_name not in module_setup:
                module_setup[plugin_name] = {}
            self.setup_merge(module_setup[plugin_name], plugin_config)
            if "pins" in module_setup[plugin_name]:
                for pin in module_setup[plugin_name]["pins"]:
                    module_setup[plugin_name]["pins"][pin]["pin_mapped"] = module_setup[plugin_name]["pins"][pin]["pin"]
                    del module_setup[plugin_name]["pins"][pin]["pin"]

            mplugins.load_plugin(plugin_id, module_setup[plugin_name], self.config)

        self.modules[slot_name] = {
            "defaults": module_defaults,
            "setup": module_setup,
            "instances": mplugins.plugin_instances,
        }

        self.config_load()
        self.tree_expand("/Modules/")

    def del_plugin(self, plugin_instance, widget, dialog=None):
        plugin_id = plugin_instance.plugin_id
        if dialog is not None:
            dialog.is_removed = True
            dialog.close()
        self.config["plugins"].pop(plugin_id)
        self.config_load()
        self.display()

    def edit_modifier(self, modifier_list, modifier_id, parent_layout=None):
        def update():
            mods = []
            for modifier_id, modifier in enumerate(modifier_list):
                modifier_type = modifier.get("type", "???")
                if dialog.modifier_id == modifier_id:
                    mods.append(modifier_type.upper())
                else:
                    mods.append(modifier_type)
            dialog.mlabel.setText(f"Chain: {'>'.join(mods)}")

        def remove_modifier():
            modifier_list.pop(dialog.modifier_id)
            if parent_layout:
                self.modifier_list_update(parent_layout, modifier_list)
            dialog.close()

        def move_left():
            if dialog.modifier_id > 0:
                modifier_list[dialog.modifier_id - 1], modifier_list[dialog.modifier_id] = modifier_list[dialog.modifier_id], modifier_list[dialog.modifier_id - 1]
                if parent_layout:
                    self.modifier_list_update(parent_layout, modifier_list)
                dialog.modifier_id -= 1
                update()

        def move_right():
            if dialog.modifier_id < len(modifier_list) - 1:
                modifier_list[dialog.modifier_id + 1], modifier_list[dialog.modifier_id] = modifier_list[dialog.modifier_id], modifier_list[dialog.modifier_id + 1]
                if parent_layout:
                    self.modifier_list_update(parent_layout, modifier_list)
                dialog.modifier_id += 1
                update()

        dialog = QDialog()
        dialog.setWindowTitle("edit Modifier")
        dialog.setStyleSheet(STYLESHEET)
        dialog.modifier_id = modifier_id
        modifier_config = modifier_list[dialog.modifier_id]
        modifier_type = modifier_config.get("type", "???")

        dialog.layout = QVBoxLayout()
        dialog_buttonBox = QDialogButtonBox(QDialogButtonBox.Ok)
        dialog_buttonBox.accepted.connect(dialog.accept)

        remove_button = QPushButton(self.tr("Remove"))
        remove_button.clicked.connect(remove_modifier)
        dialog_buttonBox.addButton(remove_button, QDialogButtonBox.ActionRole)

        if len(modifier_list) > 1:
            move_button = QPushButton(self.tr("<<"))
            move_button.clicked.connect(move_left)
            dialog_buttonBox.addButton(move_button, QDialogButtonBox.ActionRole)

            move_button = QPushButton(self.tr(">>"))
            move_button.clicked.connect(move_right)
            dialog_buttonBox.addButton(move_button, QDialogButtonBox.ActionRole)

        dialog.layout.addWidget(QLabel(f"Type: {modifier_type}"))

        if modifier_type == "onerror":
            dialog.layout.addWidget(QLabel("Invert:"))
            dialog.layout.addWidget(self.edit_item(modifier_config, "invert", {"type": bool, "default": False}, cb=None))
        elif modifier_type == "debounce":
            dialog.layout.addWidget(QLabel("Delay:"))
            dialog.layout.addWidget(self.edit_item(modifier_config, "delay", {"type": int, "default": 16}, cb=None))
        elif modifier_type == "pwm":
            dialog.layout.addWidget(QLabel("Frequency:"))
            dialog.layout.addWidget(self.edit_item(modifier_config, "frequency", {"type": int, "default": 1}, cb=None))
            dialog.layout.addWidget(QLabel("DTY:"))
            dialog.layout.addWidget(self.edit_item(modifier_config, "dty", {"type": int, "default": 50}, cb=None))

        dialog.mlabel = QLabel("")
        dialog.layout.addWidget(dialog.mlabel)
        update()

        dialog.layout.addWidget(dialog_buttonBox)
        dialog.setLayout(dialog.layout)

        if dialog.exec():
            modifier_list[dialog.modifier_id] = modifier_config

    def modifier_list_add(self, parent_layout, modifier_list):
        dialog = QDialog()
        dialog.setWindowTitle("add Modifier")
        dialog.setStyleSheet(STYLESHEET)

        dialog_buttonBox = QDialogButtonBox(QDialogButtonBox.Ok)
        dialog_buttonBox.accepted.connect(dialog.accept)

        dialog.layout = QVBoxLayout()
        label = QLabel("Modifier:")
        dialog.layout.addWidget(label)
        combo = QComboBox(self)
        for modifier_name in Modifiers().pin_modifier_list():
            combo.addItem(modifier_name)
        dialog.layout.addWidget(combo)

        dialog.layout.addWidget(dialog_buttonBox)
        dialog.setLayout(dialog.layout)

        if dialog.exec():
            modifier_type = combo.currentText()
            modifier_list.append({"type": modifier_type})
            self.modifier_list_update(parent_layout, modifier_list)
            if modifier_type != "invert":
                self.edit_modifier(modifier_list, len(modifier_list) - 1, parent_layout)

    def modifier_list_update(self, parent_layout, modifier_list):
        pc = parent_layout.count()
        for i in reversed(range(pc)):
            parent_layout.itemAt(i).widget().setParent(None)

        for modifier_id, modifier in enumerate(modifier_list):
            modifier_type = modifier.get("type", "???")
            modifier_button = QPushButton(modifier_type)
            modifier_button.clicked.connect(partial(self.edit_modifier, modifier_list, modifier_id, parent_layout))
            modifier_button.setFixedWidth(len(modifier_type) * 9 + 10)
            parent_layout.addWidget(modifier_button, stretch=1)

    def edit_plugin_pins(self, plugin_instance, plugin_config):
        def update(arg):
            print("#update", arg, plugin_config)

        myFont = QFont()
        myFont.setBold(True)

        pins = QVBoxLayout()
        label = QLabel("Pin-Setup")
        label.setFont(myFont)
        pins.addWidget(label)

        if "pins" not in plugin_config:
            plugin_config["pins"] = {}

        for pin_name, pin_defaults in plugin_instance.PINDEFAULTS.items():
            if pin_name not in plugin_config["pins"]:
                plugin_config["pins"][pin_name] = {}
            pin_config = plugin_config.get("pins", {}).get(pin_name, {})
            pin_title = pin_name
            direction = pin_defaults["direction"]
            description = pin_defaults.get("description")
            optional = pin_defaults.get("optional", False)
            help_text = f"location for {direction} pin: {pin_name}"
            if optional:
                help_text = f"{help_text} (optional)"

            if optional:
                pin_title = f"{pin_title} (optional)"

            if description:
                help_text = f"{help_text}: {description}"
                pin_title = f"{pin_title}: {description}"

            frame = QGroupBox(self)
            frame.setTitle(pin_title)
            frame.setToolTip(help_text)

            pin_rows = QVBoxLayout()

            pin_cols = QHBoxLayout()
            pin_rows.addLayout(pin_cols)
            pin_cols.addWidget(QLabel(f"Dir: {direction}"), stretch=1)

            # Options
            pin_cols = QHBoxLayout()
            pin_rows.addLayout(pin_cols)
            pin_cols.addWidget(QLabel("Pin:"), stretch=2)
            pin_cols.addWidget(self.edit_item(pin_config, "pin", {"type": "select", "options": self.pinlist, "default": ""}, cb=update), stretch=6)
            if direction == "input":
                pin_cols.addWidget(QLabel("Pull:"), stretch=1)
                pin_cols.addWidget(self.edit_item(pin_config, "pull", {"type": "select", "options": [None, "up", "down"], "default": None}, cb=update), stretch=3)
            else:
                pin_cols.addWidget(QLabel(""), stretch=4)

            # Modifiers
            if "modifier" not in pin_config:
                pin_config["modifier"] = []
            modifier_list = pin_config["modifier"]

            pin_cols = QHBoxLayout()
            pin_rows.addLayout(pin_cols)
            pin_cols.addWidget(QLabel("Modifiers:"))
            mod_cols = QHBoxLayout()
            pin_cols.addLayout(mod_cols)
            add_button = QPushButton("+")
            add_button.clicked.connect(partial(self.modifier_list_add, mod_cols, modifier_list))
            add_button.setFixedWidth(20)
            pin_cols.addWidget(add_button)
            pin_cols.addStretch()
            self.modifier_list_update(mod_cols, modifier_list)

            # IO-Standart
            pin_cols = QHBoxLayout()
            pin_rows.addLayout(pin_cols)

            io_label = QLabel("IO-Standart:")
            io_label.setToolTip("FPGA level IO config / optional / better do not use :)")
            pin_cols.addWidget(io_label, stretch=1)

            pin_cols.addWidget(
                self.edit_item(pin_config, "iostandard", {"type": "select", "options": ["LVTTL", "LVCMOS33", "LVCMOS25", "LVCMOS18", "LVCMOS15", "LVCMOS12"], "default": "LVTTL"}, cb=update), stretch=3
            )
            if direction == "output":
                pin_cols.addWidget(QLabel("Slew:"), stretch=1)
                pin_cols.addWidget(self.edit_item(pin_config, "slew", {"type": "select", "options": ["SLOW", "FAST"], "default": "SLOW"}, cb=update), stretch=3)
                pin_cols.addWidget(QLabel("Drive:"), stretch=1)
                pin_cols.addWidget(self.edit_item(pin_config, "drive", {"type": "select", "options": ["2", "4", "8", "12", "16", "24"], "default": "4"}, cb=update), stretch=3)
            else:
                pin_cols.addWidget(QLabel(""), stretch=8)

            frame.setLayout(pin_rows)
            pins.addWidget(frame)

        pins_widget = QWidget()
        pins.addStretch()
        pins_widget.setLayout(pins)

        pins_tab = QScrollArea()
        pins_tab.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        pins_tab.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        pins_tab.setWidgetResizable(True)
        pins_tab.setWidget(pins_widget)

        return pins_tab

    def draw_joint_home(self, joints_setup, joint_options):
        HOME_SEARCH_VEL = joints_setup.get("home_search_vel", joint_options["home_search_vel"].get("default", 0.0))
        HOME_OFFSET = joints_setup.get("home_offset", joint_options["home_offset"].get("default", 0.0))
        HOME = joints_setup.get("home", joint_options["home"].get("default", 0.0))

        def svg_arrow_h(x, y, x2, color="rgb(255, 255, 255)"):
            svg_data = []
            if x < x2:
                svg_data.append(f'<line x1="{x}" y1="{y}" x2="{x2}" y2="{y}" stroke="{color}" stroke-width="1"></line>')
                svg_data.append(f'<line x1="{x2}" y1="{y}" x2="{x2-10}" y2="{y-3}" stroke="{color}" stroke-width="1"></line>')
                svg_data.append(f'<line x1="{x2}" y1="{y}" x2="{x2-10}" y2="{y+3}" stroke="{color}" stroke-width="1"></line>')
            else:
                svg_data.append(f'<line x1="{x}" y1="{y}" x2="{x2}" y2="{y}" stroke="{color}" stroke-width="1"></line>')
                svg_data.append(f'<line x1="{x2}" y1="{y}" x2="{x2+10}" y2="{y-3}" stroke="{color}" stroke-width="1"></line>')
                svg_data.append(f'<line x1="{x2}" y1="{y}" x2="{x2+10}" y2="{y+3}" stroke="{color}" stroke-width="1"></line>')
            return svg_data

        def svg_line_h(x, y, w, color="rgb(255, 255, 255)"):
            return [f'<line x1="{x}" y1="{y}" x2="{x+w}" y2="{y}" stroke="{color}" stroke-width="1"></line>']

        def svg_line_v(x, y, h, color="rgb(255, 255, 255)"):
            return [f'<line x1="{x}" y1="{y}" x2="{x}" y2="{y+h}" stroke="{color}" stroke-width="1"></line>']

        def svg_text(x, y, text, center=False, color="rgb(255, 255, 255)"):
            if center:
                return [f'<text x="{x}" y="{y}" fill="{color}" text-anchor="middle">{text}</text>']
            else:
                return [f'<text x="{x}" y="{y}" fill="{color}">{text}</text>']

        y_diff = 15
        top = 12
        width = 400
        height = 6 * y_diff
        left = 95
        right = 10
        svg_data = [f'<svg width="{width}" height="{height}"><g><rect width="{width}" height="{height}" x="0" y="0" fill="black" />']

        min_pos = min(0, HOME, HOME_OFFSET) - 1.0
        max_pos = max(0, HOME, HOME_OFFSET) + 1.0

        scale_width = abs(max_pos - min_pos)
        scale = (width - left - right) / scale_width
        scale_offset = -min_pos * scale + left

        y_line = top + 3
        y_pos = top
        svg_data += svg_text(5, y_pos, "MACHINE")
        svg_data += svg_line_h(left, y_line, width - left - right)
        svg_data += svg_text(scale_offset, y_pos, "0.0", True)
        svg_data += svg_line_v(scale_offset, y_line - 2, 5)

        y_pos += y_diff
        svg_data += svg_text(5, y_pos, "OFFSET")
        svg_data += svg_text(scale_offset + HOME_OFFSET * scale, y_pos, f"{HOME_OFFSET}", True)
        svg_data += svg_line_v(scale_offset + HOME_OFFSET * scale, y_line - 2, 5)

        y_pos += y_diff
        svg_data += svg_text(5, y_pos, "HOME")
        svg_data += svg_text(scale_offset + HOME * scale, y_pos, f"{HOME}", True)
        svg_data += svg_line_v(scale_offset + HOME * scale, y_line - 2, 5)

        y_pos += y_diff
        svg_data += svg_text(5, y_pos, "SEARCH_VEL")
        if HOME_SEARCH_VEL > 0:
            svg_data += svg_arrow_h(scale_offset + (max_pos - 0.2) * scale, y_pos - 3, scale_offset + HOME_OFFSET * scale)
        else:
            svg_data += svg_arrow_h(scale_offset + (min_pos + 0.2) * scale, y_pos - 3, scale_offset + HOME_OFFSET * scale)

        y_pos += y_diff
        svg_data += svg_text(5, y_pos, "LATCH_VEL")
        svg_data += svg_arrow_h(scale_offset + HOME_OFFSET * scale - 2, y_pos - 3 - (y_diff / 2), scale_offset + HOME_OFFSET * scale + 22, color="rgb(200, 100, 100)")
        svg_data += svg_arrow_h(scale_offset + HOME_OFFSET * scale + 22, y_pos - 3, scale_offset + HOME_OFFSET * scale)

        y_pos += y_diff
        svg_data += svg_text(5, y_pos, "FINAL_VEL")
        svg_data += svg_arrow_h(scale_offset + HOME_OFFSET * scale, y_pos - 3, scale_offset + HOME * scale)

        svg_data.append("</g></svg>")
        return "\n".join(svg_data).encode()

    def edit_plugin_joints(self, plugin_instance, plugin_config):
        def update(arg):
            svgWidget.load(self.draw_joint_home(joints_setup, joint_options))

        myFont = QFont()
        myFont.setBold(True)

        if "joint" not in plugin_config:
            plugin_config["joint"] = {}
        joints_setup = plugin_config["joint"]

        joint_options = copy.deepcopy(halpins.JOINT_OPTIONS)

        for key, value in riocore.generator.LinuxCNC.LinuxCNC.JOINT_DEFAULTS.items():
            key = key.lower()
            if key == "scale_out":
                key = "scale"
            if key in joint_options:
                joint_options[key.lower()]["default"] = value

        joint_tabs = QTabWidget()

        general_layout = QVBoxLayout()
        label = QLabel("Joint-Setup")
        label.setFont(myFont)
        general_layout.addWidget(label)

        for option, option_setup in joint_options.items():
            if option.startswith("home"):
                continue
            tootltip = halpins.INI_HELPTEXT["JOINT_NUM"].get(option.upper(), f"{option} config")
            option_row = QHBoxLayout()
            option_label = QLabel(option.replace("_", "-").title())
            option_label.setToolTip(tootltip)
            option_row.addWidget(option_label, stretch=1)

            if option == "feedback":
                options = [""]
                for plugin_instance in self.plugins.plugin_instances:
                    for signal_name, signal_config in plugin_instance.signals().items():
                        if signal_name == "position":
                            options.append(f"{plugin_instance.title}:{signal_name}")
                option_setup = {"type": "select", "options": options, "default": ""}
                option_widget = self.edit_item(joints_setup, option, option_setup, cb=update)
            else:
                option_widget = self.edit_item(joints_setup, option, option_setup, cb=update)

            option_row.addWidget(option_widget, stretch=3)
            general_layout.addLayout(option_row)

        general_tab = QWidget()
        general_layout.addStretch()
        general_tab.setLayout(general_layout)
        joint_tabs.addTab(general_tab, "General")

        homing_layout = QVBoxLayout()
        label = QLabel("Joint-Homing")
        label.setFont(myFont)
        homing_layout.addWidget(label)
        for option, option_setup in joint_options.items():
            if not option.startswith("home"):
                continue
            tootltip = halpins.INI_HELPTEXT["JOINT_NUM"].get(option.upper(), f"{option} config")
            option_row = QHBoxLayout()
            option_label = QLabel(option.replace("_", "-").title())
            option_label.setToolTip(tootltip)
            option_row.addWidget(option_label, stretch=1)
            option_widget = self.edit_item(joints_setup, option, option_setup, cb=update)
            option_row.addWidget(option_widget, stretch=3)
            homing_layout.addLayout(option_row)

        svgWidget = QtSvg.QSvgWidget()
        update(None)
        homing_layout.addStretch()
        homing_layout.addWidget(svgWidget)

        homing_tab = QWidget()
        homing_tab.setLayout(homing_layout)
        joint_tabs.addTab(homing_tab, "Homing")

        return joint_tabs

    def edit_plugin_signals(self, plugin_instance, plugin_config):
        def update(arg):
            print("#update", arg, plugin_config)

        def toggleGroup(ctrl):
            state = ctrl.isChecked()
            if state:
                ctrl.setFixedHeight(ctrl.sizeHint().height())
            else:
                ctrl.setFixedHeight(30)

        myFont = QFont()
        myFont.setBold(True)

        signals = QVBoxLayout()
        label = QLabel("Signals-Setup")
        label.setFont(myFont)
        signals.addWidget(label)

        if "signals" not in plugin_config:
            plugin_config["signals"] = {}
        signals_setup = plugin_config["signals"]

        for signal_name, signal_defaults in plugin_instance.SIGNALS.items():
            # signal_table.setRowCount(row_n + 1)
            if signal_name not in signals_setup:
                signals_setup[signal_name] = {}
            help_text = f"{signal_name} config"

            signal_setup = signal_defaults.get("setup", {})
            signal_direction = signal_defaults["direction"]
            signal_multiplexed = signal_defaults.get("multiplexed", False)
            is_bool = signal_defaults.get("bool", False)

            options_net = []
            for halpin, halpin_info in halpins.LINUXCNC_SIGNALS[signal_direction].items():
                if is_bool:
                    if halpin_info.get("type") == bool:
                        options_net.append(halpin)
                elif halpin_info.get("type") != bool:
                    options_net.append(halpin)

            options_func = []
            for halpin, halpin_info in halpins.RIO_FUNCTIONS[signal_direction].items():
                if is_bool:
                    if halpin_info.get("type") == bool:
                        options_func.append(halpin)
                elif halpin_info.get("type") != bool:
                    options_func.append(halpin)

            frame = QGroupBox(self)
            frame.setTitle(signal_name)
            frame.setToolTip(help_text)

            signal_cols = QHBoxLayout()
            signal_rows = QVBoxLayout()
            signal_rows.addLayout(signal_cols)
            frame.setLayout(signal_rows)
            signals.addWidget(frame)

            if is_bool:
                signal_cols.addWidget(QLabel("Type: BOOL"), stretch=1)
            else:
                signal_cols.addWidget(QLabel("Type: FLOAT"), stretch=1)

            signal_cols.addWidget(QLabel(f"Dir: {signal_direction}"), stretch=1)

            if signal_multiplexed:
                signal_cols.addWidget(QLabel("Multiplexed: YES"), stretch=1)
            else:
                signal_cols.addWidget(QLabel("Multiplexed: NO"), stretch=1)

            signal_cols = QHBoxLayout()
            signal_rows.addLayout(signal_cols)
            signal_cols.addWidget(QLabel("Net:"), stretch=1)
            signal_setup["net"] = {"type": "select", "options": options_net}
            signal_cols.addWidget(self.edit_item(signals_setup[signal_name], "net", signal_setup["net"], cb=update), stretch=5)

            signal_cols = QHBoxLayout()
            signal_rows.addLayout(signal_cols)
            signal_cols.addWidget(QLabel("Function:"), stretch=1)
            signal_setup["function"] = {"type": "select", "options": options_func}
            signal_cols.addWidget(self.edit_item(signals_setup[signal_name], "function", signal_setup["function"], cb=update), stretch=5)

            if signal_direction == "output":
                signal_cols.addWidget(QLabel("setp:"), stretch=1)
                signal_setup["setp"] = {"type": str, "default": ""}
                signal_cols.addWidget(self.edit_item(signals_setup[signal_name], "setp", signal_setup["setp"], cb=update), stretch=1)

            signal_cols = QHBoxLayout()
            signal_rows.addLayout(signal_cols)

            if "source" not in signal_defaults and not signal_defaults.get("bool"):
                signal_cols.addWidget(QLabel("Scale"), stretch=1)
                signal_setup["scale"] = {"type": float, "default": 1.0}
                signal_cols.addWidget(self.edit_item(signals_setup[signal_name], "scale", signal_setup["scale"], cb=update), stretch=4)

                signal_cols.addWidget(QLabel("Offset"), stretch=1)
                signal_setup["offset"] = {"type": float, "default": 0.0}
                signal_cols.addWidget(self.edit_item(signals_setup[signal_name], "offset", signal_setup["offset"], cb=update), stretch=5)

            display_frame = QGroupBox(self)
            display_frame.setTitle("Display")
            display_frame.setToolTip(help_text)
            display_frame.setCheckable(True)
            display_frame.setChecked(False)
            toggleGroup(display_frame)
            display_frame.toggled.connect(partial(toggleGroup, display_frame))
            display_rows = QVBoxLayout()
            display_frame.setLayout(display_rows)
            signal_rows.addWidget(display_frame)

            if "display" not in signals_setup[signal_name]:
                signals_setup[signal_name]["display"] = {}
            direction = signal_defaults["direction"]
            virtual = signal_defaults.get("virtual", False)
            if virtual:
                # swap direction vor virt signals in component
                if direction == "input":
                    direction = "output"
                else:
                    direction = "input"

            if direction == "input" or signals_setup[signal_name].get("net"):
                if signal_defaults.get("bool"):
                    type_options = ["none", "led", "rectled"]
                else:
                    type_options = ["none", "number", "bar", "meter"]
            else:
                if signal_defaults.get("bool"):
                    type_options = ["none", "checkbutton", "button"]
                else:
                    type_options = ["none", "scale", "spinbox", "dial", "jogwheel"]
            display_setup = {
                "title": {"type": str},
                "section": {"type": str},
                "type": {"type": "select", "options": type_options},
            }
            if not signal_defaults.get("bool", False):
                display_setup["min"] = {"type": float, "default": None}
                display_setup["max"] = {"type": float, "default": None}
            for option, option_setup in display_setup.items():
                display_cols = QHBoxLayout()
                display_rows.addLayout(display_cols)
                display_cols.addWidget(QLabel(option.title()), stretch=1)
                display_cols.addWidget(self.edit_item(signals_setup[signal_name]["display"], option, option_setup, cb=None), stretch=5)

        signals_widget = QWidget()
        signals.addStretch()
        signals_widget.setLayout(signals)

        signals_tab = QScrollArea()
        signals_tab.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        signals_tab.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        signals_tab.setWidgetResizable(True)
        signals_tab.setWidget(signals_widget)
        return signals_tab

    def edit_plugin_options(self, plugin_instance, plugin_config):
        def update(arg):
            plugin_instance.update_title()
            iname_label.setText(plugin_instance.title)

        myFont = QFont()
        myFont.setBold(True)

        options = QVBoxLayout()

        infotext = plugin_instance.INFO
        label = QLabel(f"{infotext}\n")
        label.setFont(myFont)
        options.addWidget(label)

        iname_row = QHBoxLayout()
        iname_row.addWidget(QLabel("Instance-Name"), stretch=1)
        iname_label = QLabel(plugin_instance.title)
        iname_row.addWidget(iname_label, stretch=3)
        options.addLayout(iname_row)

        for option_name, option_defaults in plugin_instance.OPTIONS.items():
            title = option_name.title()
            unit = option_defaults.get("unit")
            if unit:
                title = f"{title} ({unit})"
            help_text = option_defaults.get("description", title)
            option_row = QHBoxLayout()
            options.addLayout(option_row)
            option_label = QLabel(title)
            option_label.setToolTip(help_text)
            option_row.addWidget(option_label, stretch=1)
            option_row.addWidget(self.edit_item(plugin_config, option_name, option_defaults, cb=update), stretch=3)

        if plugin_instance.PLUGIN_CONFIG:
            button_config = QPushButton("config")
            cb = partial(self.config_plugin, plugin_instance, plugin_instance.plugin_id)
            button_config.clicked.connect(cb)
            button_config.setMaximumSize(button_config.sizeHint())
            options.addWidget(button_config)

        descriptiontext = plugin_instance.DESCRIPTION
        label = QLabel(f"{descriptiontext}\n")
        options.addWidget(label)

        options_widget = QWidget()
        options.addStretch()
        options_widget.setLayout(options)

        options_tab = QScrollArea()
        options_tab.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        options_tab.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        options_tab.setWidgetResizable(True)
        options_tab.setWidget(options_widget)
        return options_tab

    def edit_plugin(self, plugin_instance, widget, is_new=False, nopins=False):
        plugin_config = plugin_instance.plugin_setup
        plugin_config_backup = copy.deepcopy(plugin_config)

        dialog = QDialog()
        dialog.is_removed = False
        dialog.setWindowTitle(f"edit Plugin {plugin_instance.NAME}")
        dialog.setStyleSheet(STYLESHEET)
        dialog_buttonBox = QDialogButtonBox(QDialogButtonBox.Cancel | QDialogButtonBox.Ok)
        dialog_buttonBox.accepted.connect(dialog.accept)
        dialog_buttonBox.rejected.connect(dialog.reject)

        if self.config["linuxcnc"].get("gui", "axis") == "axis":
            pyvcp_button = QPushButton(self.tr("PyVCP-Preview"))
            pyvcp_button.clicked.connect(self.open_pyvcp)
            dialog_buttonBox.addButton(pyvcp_button, QDialogButtonBox.ActionRole)

        if not nopins:
            remove_button = QPushButton(self.tr("Remove"))
            remove_button.clicked.connect(partial(self.del_plugin, plugin_instance, dialog=dialog))
            dialog_buttonBox.addButton(remove_button, QDialogButtonBox.ActionRole)

        tab_widget = QTabWidget()

        options_tab = self.edit_plugin_options(plugin_instance, plugin_config)
        tab_widget.addTab(options_tab, "Plugin")

        if not nopins:
            pins_tab = self.edit_plugin_pins(plugin_instance, plugin_config)
            tab_widget.addTab(pins_tab, "Pins")
            if is_new:
                tab_widget.setCurrentWidget(pins_tab)

        if plugin_instance.TYPE == "joint" and plugin_config.get("is_joint", False):
            joint_tab = self.edit_plugin_joints(plugin_instance, plugin_config)
            tab_widget.addTab(joint_tab, "Joint")
        elif plugin_instance.TYPE != "interface":
            if plugin_instance.SIGNALS:
                signals_tab = self.edit_plugin_signals(plugin_instance, plugin_config)
                tab_widget.addTab(signals_tab, "Signals")

        right_layout = QVBoxLayout()
        plugin_path = f"{riocore_path}/plugins/{plugin_instance.NAME}"
        image_path = f"{plugin_path}/image.png"
        if os.path.isfile(image_path):
            ilabel = QLabel(self)
            pixmap = QPixmap(image_path)
            ilabel.setPixmap(pixmap)
            right_layout.addWidget(ilabel)
            right_layout.addStretch()

        hlayout = QHBoxLayout()
        hlayout.addWidget(tab_widget)
        hlayout.addLayout(right_layout)

        dialog_layout = QVBoxLayout()
        dialog_layout.addLayout(hlayout)
        dialog_layout.addWidget(dialog_buttonBox)
        dialog.setLayout(dialog_layout)

        if dialog.exec():
            self.config_load()
            self.display()
            return
        if not dialog.is_removed:
            for key in plugin_config:
                if key not in plugin_config_backup:
                    del plugin_config[key]
            for key in plugin_config_backup:
                plugin_config[key] = plugin_config_backup[key]

    def config_plugin(self, plugin_instance, plugin_id, widget):
        if os.path.isfile(f"{riocore_path}/plugins/{plugin_instance.NAME}/config.py"):
            plugin_config = importlib.import_module(".config", f"riocore.plugins.{plugin_instance.NAME}")
            config_box = plugin_config.config(plugin_instance, styleSheet=STYLESHEET)
            config_box.run()
        self.config_load()
        self.load_tree()
        self.display()

    def select_module(self, last_error=None, set_slot=None, set_module=None, slot_select=True):
        dialog = QDialog()
        dialog.setWindowTitle("add Module")
        dialog.setStyleSheet(STYLESHEET)

        dialog_buttonBox = QDialogButtonBox(QDialogButtonBox.Cancel | QDialogButtonBox.Ok)
        dialog_buttonBox.accepted.connect(dialog.accept)
        dialog_buttonBox.rejected.connect(dialog.reject)

        dialog.layout = QVBoxLayout()
        if last_error:
            message = QLabel(last_error)
            dialog.layout.addWidget(message)

        label = QLabel("Slot:")
        dialog.layout.addWidget(label)
        combo_slot = QComboBox(self)
        combo_slot.setDisabled(not slot_select)
        dialog.layout.addWidget(combo_slot)

        label = QLabel("Module:")
        dialog.layout.addWidget(label)
        combo_module = QComboBox(self)

        item = 0
        for slot in self.slots:
            slot_name = slot["name"]
            if slot_name not in self.modules:
                combo_slot.addItem(slot_name)
                if slot_name == set_slot:
                    combo_slot.setCurrentIndex(item)
                item += 1

        item = 0
        for module_name in self.module_names:
            combo_module.addItem(module_name)
            if module_name == set_module:
                combo_module.setCurrentIndex(item)
            item += 1

        dialog.layout.addWidget(combo_module)

        dialog.layout.addWidget(dialog_buttonBox)
        dialog.setLayout(dialog.layout)

        if dialog.exec():
            return (combo_slot.currentText(), combo_module.currentText())

    def flash_cb(self):
        self.tabwidget.setCurrentWidget(self.tabs["Gateware"].widget())
        self.tabs["Gateware"].setTab("Flash-Output")

        widget = self.tabs["Gateware"].gateware["Flash-Output"]
        config_name = self.config.get("name")
        widget.clear()
        widget.insertPlainText("...")

        self.flash_start = time.time()
        self.flash_sub = subprocess.Popen(f"(cd Output/{config_name}/Gateware/ ; make load 2>&1 | tee flash.log)", shell=True, close_fds=True)
        self.button_flash.setEnabled(False)
        self.info_widget.setText("flashing...")

    def compile_cb(self):
        self.tabwidget.setCurrentWidget(self.tabs["Gateware"].widget())
        self.tabs["Gateware"].setTab("Compile-Output")

        widget = self.tabs["Gateware"].gateware["Compile-Output"]
        config_name = self.config.get("name")
        widget.clear()
        widget.insertPlainText("...")

        self.compile_start = time.time()
        self.compile_sub = subprocess.Popen(f"(cd Output/{config_name}/Gateware/ ; make clean all 2>&1 | tee compile.log)", shell=True, close_fds=True)
        self.button_compile.setEnabled(False)
        self.info_widget.setText("compiling...")

    def generate_cb(self, preview=False):
        self.info_widget.setText("generate...")
        self.output_path = "Output"
        if preview:
            self.output_path = "OutputTMP"

        self.generate(self.output_path, preview=preview)
        try:
            self.tabs["Gateware"].update()
            self.tabs["LinuxCNC"].update()
            self.tabs["Hal"].update()

        except Exception as error:
            print(f"ERROR loading output: {error}")

        if preview:
            os.system(f"rm -rf {self.output_path}/")
        self.info_widget.setText("generate...done")

    def generate(self, output_path=None, preview=False):
        config = self.clean_config(self.config)
        if not output_path:
            output_path = "Output"
        try:
            if preview:
                open(f"{self.config_file}_tmp.json", "w").write(json.dumps(config, indent=4))
                os.system(f"{riocore_path}/../bin/rio-generator -p {self.config_file}_tmp.json {output_path} >/dev/null")
                os.system(f"rm {self.config_file}_tmp.json")
            else:
                os.system(f"{riocore_path}/../bin/rio-generator {self.config_file} {output_path}")
                self.check_status()
        except Exception as error:
            print(f"ERROR generating output: {error}")

    def save_config_as(self, widget=None):
        file_dialog = QFileDialog(self)
        file_dialog.setNameFilters(["json (*.json)"])

        if self.config_file:
            name = file_dialog.getSaveFileName(self, "Save File", self.config_file, "json (*.json)")
        else:
            name = file_dialog.getSaveFileName(self, "Save File", f"{riocore_path}/configs/", "json (*.json)")

        if name[0]:
            if not name[0].endswith(".json"):
                name[0] = f"{name[0]}.json"
            self.save_config(name[0])
            self.config_file = name[0]
            self.config_original = self.clean_config(self.config)
            self.info_widget.setText(f"Saved as: {os.path.basename(name[0])}")
            self.check_status()

    def save_config_cb(self):
        self.save_config(self.config_file)
        if self.config_file is not None:
            self.config_original = self.clean_config(self.config)
            self.info_widget.setText(f"Saved as: {os.path.basename(self.config_file)}")
            self.check_status()
        else:
            print("ERROR: saving config")
            self.info_widget.setText("ERROR: saving config")

    def save_config(self, filename):
        if filename is None:
            self.save_config_as()
        else:
            config = self.clean_config(self.config)
            open(filename, "w").write(json.dumps(config, indent=4))

    def tree_add_plugin(self, parent, plugin_instance, nopins=False, expand=False):
        name = plugin_instance.plugin_setup.get("name")
        title = plugin_instance.NAME
        if name:
            title = f"{name} ({plugin_instance.NAME})"
        else:
            title = f"{plugin_instance.title} ({plugin_instance.NAME})"
        help_text = plugin_instance.INFO

        aitem = MyStandardItem()
        parent.appendRow(
            [
                MyStandardItem(title, help_text=help_text),
                aitem,
            ]
        )

        buttons_layout = QHBoxLayout()
        buttons_layout.setContentsMargins(0, 0, 0, 0)
        buttons_widget = QWidget()
        buttons_widget.setLayout(buttons_layout)

        button_edit = QPushButton("edit")
        cb = partial(self.edit_plugin, plugin_instance, nopins=nopins)
        button_edit.clicked.connect(cb)
        button_edit.setMaximumSize(button_edit.sizeHint())
        buttons_layout.addWidget(button_edit)

        if not nopins:
            button_delete = QPushButton("delete")
            cb = partial(self.del_plugin, plugin_instance)
            button_delete.clicked.connect(cb)
            button_delete.setMaximumSize(button_delete.sizeHint())
            buttons_layout.addWidget(button_delete)

        if plugin_instance.PLUGIN_CONFIG:
            button_config = QPushButton("config")
            cb = partial(self.config_plugin, plugin_instance, plugin_instance.plugin_id)
            button_config.clicked.connect(cb)
            button_config.setMaximumSize(button_config.sizeHint())
            buttons_layout.addWidget(button_config)
        buttons_layout.addStretch()
        self.treeview.setIndexWidget(aitem.index(), buttons_widget)

    def callback_plugin_name(self, parent, plugin_instance, value):
        parent.setText(f"{value} ({plugin_instance.NAME})")

    def pin_edit_cb(self, widget):
        print("pin_edit_cb")
        self.generate_cb(preview=True)
        # self.request_load_tree = 3
        self.tabs["Overview"].update()
        self.tabs["Pins"].update()
        self.tabs["Json"].update()


def main():
    app = QApplication(sys.argv)

    parser = argparse.ArgumentParser()
    parser.add_argument("config", help="config", nargs="?", type=str, default=None)
    parser.add_argument("--nostyle", "-n", help="disable stylesheets", default=False, action="store_true")
    args = parser.parse_args()

    if args.nostyle:
        STYLESHEET = ""

    form = WinForm(args)
    form.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()