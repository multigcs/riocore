import copy
import json
import os

import riocore


from riocore.gui.widgets import (
    STYLESHEET,
)

from PyQt5.QtGui import QFont, QPixmap
from PyQt5.QtWidgets import (
    QDialog,
    QComboBox,
    QMessageBox,
    QWidget,
    QDialogButtonBox,
    QHBoxLayout,
    QLabel,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
)

riocore_path = os.path.dirname(riocore.__file__)


class GuiModules:
    def __init__(self, parent):
        self.parent = parent

    def del_module(self, slot_name):
        for mn, module_data in enumerate(self.parent.config.get("modules", [])):
            if slot_name == module_data.get("slot"):
                self.parent.config["modules"].pop(mn)
                break
        self.parent.config_load()
        # self.parent.display()
        self.parent.tree_expand("/Modules/")

    def split_module(self, slot_name):
        for mn, module_data in enumerate(self.parent.config.get("modules", [])):
            if slot_name == module_data.get("slot"):
                # split module into plugins
                if module_data.get("setup") is None:
                    module_name = module_data.get("module")
                    module_path = self.parent.get_path(os.path.join("modules", module_name, "module.json"))
                    moduleJsonStr = open(module_path, "r").read()
                    module_defaults = json.loads(moduleJsonStr)
                    module_data["setup"] = {}
                    for plugin in module_defaults.get("plugins", []):
                        new_plugin = copy.deepcopy(plugin)
                        for pin_name, pin_data in new_plugin.get("pins", {}).items():
                            pin = pin_data["pin"]
                            new_plugin["pins"][pin_name]["pin"] = f"{slot_name}:{pin}"
                        self.parent.config["plugins"].append(new_plugin)
                else:
                    for sname, setup_data in module_data.get("setup", {}).items():
                        for pin_name, pin_data in setup_data.get("pins", {}).items():
                            pin_mapped = pin_data.get("pin_mapped")
                            if pin_mapped:
                                setup_data["pins"][pin_name]["pin"] = f"{slot_name}:{pin_mapped}"
                                del setup_data["pins"][pin_name]["pin_mapped"]
                        self.parent.config["plugins"].append(copy.deepcopy(setup_data))

                # remove module
                self.parent.config["modules"].pop(mn)
                break
        self.parent.config_load()
        # self.parent.display()
        self.parent.tree_expand("/Modules/")

    def add_module(self, widget, slot_name=None, module_name=None, slot_select=True):
        last_error = None
        while True:
            ret = self.select_module(last_error=last_error, set_slot=slot_name, set_module=module_name, slot_select=slot_select)
            if not ret:
                return
            slot_name, module_name = ret
            if not module_name or not slot_name:
                return

            module_path = self.parent.get_path(os.path.join("modules", module_name, "module.json"))
            moduleJsonStr = open(module_path, "r").read()
            module_defaults = json.loads(moduleJsonStr)

            slot_setup = {}
            for slot in self.parent.slots:
                if slot_name == slot["name"]:
                    slot_setup = slot
            slot_pins = slot_setup.get("pins", {})

            check = True
            for plugin in module_defaults.get("plugins"):
                for pin_name, pin_config in plugin.get("pins", {}).items():
                    pin_location = pin_config.get("pin")
                    if "[" in pin_location:
                        continue
                    if pin_location not in slot_pins:
                        check = False

            if check is True:
                break
            else:
                last_error = "ERROR: module/slot is not compatible"
                print(last_error)

        if "modules" not in self.parent.config:
            self.parent.config["modules"] = []

        module_setup = {}
        self.parent.config["modules"].append(
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
            self.parent.setup_merge(module_setup[plugin_name], plugin_config)
            if "pins" in module_setup[plugin_name]:
                for pin in module_setup[plugin_name]["pins"]:
                    module_setup[plugin_name]["pins"][pin]["pin_mapped"] = module_setup[plugin_name]["pins"][pin]["pin"]
                    del module_setup[plugin_name]["pins"][pin]["pin"]

            mplugins.load_plugin(plugin_id, module_setup[plugin_name], self.parent.config)

        self.parent.modules[slot_name] = {
            "defaults": module_defaults,
            "setup": module_setup,
            "instances": mplugins.plugin_instances,
        }

        self.parent.config_load()
        self.parent.tree_expand("/Modules/")

    def select_module(self, last_error=None, set_slot=None, set_module=None, slot_select=True):
        dialog = QDialog()
        dialog.setWindowTitle("select module")
        dialog.setStyleSheet(STYLESHEET)

        dialog.layout = QVBoxLayout()
        dialog_buttonBox = QDialogButtonBox(QDialogButtonBox.Cancel | QDialogButtonBox.Ok)
        dialog_buttonBox.accepted.connect(dialog.accept)
        dialog_buttonBox.rejected.connect(dialog.reject)
        dialog.setLayout(dialog.layout)

        dialog.module_names = []

        def show_module_info(idx):
            module_name = dialog.module_names[idx]
            module_path = os.path.join(riocore_path, "modules", module_name)
            moduleJsonStr = open(os.path.join(module_path, "module.json"), "r").read()
            module_defaults = json.loads(moduleJsonStr)
            image_path = os.path.join(module_path, "module.png")
            if os.path.isfile(image_path):
                pixmap = QPixmap(image_path)
                image_label.setPixmap(pixmap)
            else:
                image_label.clear()
            name_label.setText(f"Name: {module_name}")
            description = module_defaults.get("comment", "")
            description_label.setText(description)
            dialog.selected = module_name

        module_table = QTableWidget()
        module_table.setColumnCount(1)
        module_table.setHorizontalHeaderItem(0, QTableWidgetItem("Modules"))

        if not slot_select:
            slot_setup = {}
            for slot in self.parent.slots:
                if set_slot == slot["name"]:
                    slot_setup = slot
            slot_pins = slot_setup.get("pins", {})

        row_n = 0
        for module_name in self.parent.module_names:
            check = True
            if not slot_select:
                module_path = self.parent.get_path(os.path.join("modules", module_name, "module.json"))
                moduleJsonStr = open(module_path, "r").read()
                module_defaults = json.loads(moduleJsonStr)
                for plugin in module_defaults.get("plugins"):
                    for pin_name, pin_config in plugin.get("pins", {}).items():
                        pin_location = pin_config.get("pin")
                        if "[" in pin_location:
                            continue
                        if pin_location not in slot_pins:
                            check = False

            if check is True:
                module_table.setRowCount(row_n + 1)
                pitem = QTableWidgetItem(module_name)
                module_table.setItem(row_n, 0, pitem)
                dialog.module_names.append(module_name)
                row_n += 1

        header = module_table.horizontalHeader()
        header.setStretchLastSection(True)
        # module_table.setFixedWidth(200)
        module_table.cellClicked.connect(show_module_info)
        module_table.currentCellChanged.connect(show_module_info)

        left_layout = QVBoxLayout()
        left_widget = QWidget()
        # left_widget.setFixedWidth(400)
        left_widget.setLayout(left_layout)

        if last_error:
            message = QLabel(last_error)
            dialog.layout.addWidget(message)

        combo_label = QLabel("Slot:")
        left_layout.addWidget(combo_label)
        combo_slot = QComboBox()
        combo_slot.setDisabled(not slot_select)
        left_layout.addWidget(combo_slot)
        left_layout.addWidget(module_table)
        item = 0
        for slot in self.parent.slots:
            slot_name = slot["name"]
            if slot_name not in self.parent.modules:
                combo_slot.addItem(slot_name)
                if slot_name == set_slot:
                    combo_slot.setCurrentIndex(item)
                item += 1

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
        image_label = QLabel()
        right_layout.addWidget(image_label)
        right_layout.addStretch()

        infos = QHBoxLayout()
        infos.addWidget(left_widget, stretch=0)
        infos.addWidget(mid_widget, stretch=3)
        infos.addWidget(right_widget, stretch=1)

        dialog.layout.addLayout(infos)
        dialog.layout.addWidget(dialog_buttonBox)

        if not dialog.module_names:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)
            msg.setText("no matching modules found")
            msg.setWindowTitle("Warning")
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec_()
        else:
            show_module_info(0)
            if dialog.exec():
                return (combo_slot.currentText(), dialog.selected)

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
            if self.parent.board:
                self.parent.tabs["Board"].update()
                if not self.parent.args.nographs:
                    self.parent.tabs["Pins"].update()
                    self.parent.tabs["Signals"].update()
            self.parent.tabs["GPIOs"].update()
            self.parent.display()
