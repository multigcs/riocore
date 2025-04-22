import os
import re
import sys

import riocore


from PyQt5.QtWidgets import (
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
)


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
                    if "[" not in pin:
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

        for row_n, row in enumerate(table_data):
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
