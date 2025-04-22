import os
import re
import sys

import riocore

from riocore import halpins


from PyQt5.QtWidgets import (
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
)


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

                    if "signals" not in plugin_instance.setup_object:
                        plugin_instance.setup_object["signals"] = {}
                    if signal_name not in plugin_instance.setup_object["signals"]:
                        plugin_instance.setup_object["signals"][signal_name] = {}
                    setup_object = plugin_instance.setup_object["signals"][signal_name]

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
                            if halpin_info.get("type") is bool:
                                options_net.append(halpin)
                        elif halpin_info.get("type") is not bool:
                            options_net.append(halpin)

                    options_func = []
                    for halpin, halpin_info in halpins.RIO_FUNCTIONS[signal_direction].items():
                        if is_bool:
                            if halpin_info.get("type") is bool:
                                options_func.append(halpin)
                        elif halpin_info.get("type") is not bool:
                            options_func.append(halpin)

                    if key == "function":
                        widget = self.parent.edit_item(setup_object, "function", {"type": "select", "options": options_func, "default": ""}, need_enter=True, cb=self.sig_edit_cb)
                    elif key == "setp":
                        widget = self.parent.edit_item(setup_object, "setp", {"type": str, "default": ""}, need_enter=True, cb=self.sig_edit_cb)
                    else:
                        widget = self.parent.edit_item(setup_object, "net", {"type": "select", "options": options_net, "default": ""}, need_enter=True, cb=self.sig_edit_cb)

                    table_data.append(
                        (f"rio.{signal_halname}", {"output": "<-", "input": "->", "inout": "<->"}.get(signal_direction, signal_direction), signal_net, htype, key, plugin_instance, signal_name, widget)
                    )

        for plugin_instance in self.parent.plugins.plugin_instances:
            for signal_name, signal_config in plugin_instance.signals().items():
                signal_direction = signal_config["direction"]
                signal_halname = signal_config["halname"]

                if "signals" not in plugin_instance.setup_object:
                    plugin_instance.setup_object["signals"] = {}
                if signal_name not in plugin_instance.setup_object["signals"]:
                    plugin_instance.setup_object["signals"][signal_name] = {}
                setup_object = plugin_instance.setup_object["signals"][signal_name]

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

                options_net = [""]
                for halpin, halpin_info in halpins.LINUXCNC_SIGNALS[signal_direction].items():
                    if is_bool:
                        if halpin_info.get("type") is bool:
                            options_net.append(halpin)
                    elif halpin_info.get("type") is not bool:
                        options_net.append(halpin)

                options_func = [""]
                for halpin, halpin_info in halpins.RIO_FUNCTIONS[signal_direction].items():
                    if is_bool:
                        if halpin_info.get("type") is bool:
                            options_func.append(halpin)
                    elif halpin_info.get("type") is not bool:
                        options_func.append(halpin)

                if key == "function":
                    widget = self.parent.edit_item(setup_object, "function", {"type": "select", "options": options_func, "default": ""}, need_enter=True, cb=self.sig_edit_cb)
                elif key == "setp":
                    widget = self.parent.edit_item(setup_object, "setp", {"type": str, "default": ""}, need_enter=True, cb=self.sig_edit_cb)
                else:
                    widget = self.parent.edit_item(setup_object, "net", {"type": "select", "options": options_net, "default": ""}, need_enter=True, cb=self.sig_edit_cb)

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
