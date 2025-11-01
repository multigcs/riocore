import os
import glob

import copy
from functools import partial

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QStandardItemModel
from PyQt5.QtWidgets import (
    QLineEdit,
    QSplitter,
    QPlainTextEdit,
    QDialogButtonBox,
    QScrollArea,
    QDoubleSpinBox,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QTreeView,
    QTabWidget,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
    QDialog,
)


import riocore
from riocore.gui.widgets import MyStandardItem
from riocore.gui.home_helper import HomeAnimation

riocore_path = os.path.dirname(riocore.__file__)


class TabDrawing:
    def __init__(self, parent):
        self.plugins = None
        self.parent = parent
        info_vbox = QWidget()
        info_vbox_layout = QVBoxLayout()
        info_vbox.setLayout(info_vbox_layout)
        self.pininfo = QPlainTextEdit("")
        info_vbox_layout.addWidget(self.pininfo)
        self.infobox = QPlainTextEdit()
        self.infobox.setLineWrapMode(QPlainTextEdit.NoWrap)
        self.infobox.setMinimumWidth(300)
        info_vbox_layout.addWidget(self.infobox)

        self.drawing_tab = QSplitter(Qt.Horizontal)
        self.drawing_tab.addWidget(self.plugin_selector())
        self.drawing_tab.addWidget(parent.view)
        self.drawing_tab.addWidget(info_vbox)

    def plugin_selector(self):
        self.plugin_table = QTableWidget()

        plugin_vbox_widget = QWidget()
        plugin_vbox_widget.plugin_search = self.plugin_table
        plugin_vbox = QVBoxLayout()
        plugin_vbox_widget.setLayout(plugin_vbox)

        self.search_text = QLineEdit("")
        self.search_text.textChanged.connect(self.plugin_search)
        plugin_vbox.addWidget(self.search_text)
        plugin_vbox.addWidget(self.plugin_table)

        def plugin_select(idx):
            if not self.plugin_table.item(idx, 0):
                return
            self.plugin_name_selected = self.plugin_table.item(idx, 0).text()
            self.plugin_info(self.plugin_name_selected)

        def plugin_update(misc):
            pass

        def plugin_add(misc):
            node_type = None
            if " " in self.plugin_name_selected:
                self.plugin_name_selected, node_type = self.plugin_name_selected.split(" ")

            psetup = {"type": self.plugin_name_selected}
            if node_type:
                psetup["node_type"] = node_type
            self.plugins.load_plugin(self.plugin_name_selected, psetup, self.parent.config)
            plugin_instance = self.plugins.plugin_instances[-1]
            if not node_type:
                if "node_type" in plugin_instance.OPTIONS:
                    option_data = plugin_instance.OPTIONS["node_type"]
                    node_type = self.parent.dialog_select("Plugin node select", option_data["options"])
                    if node_type:
                        plugin_instance.plugin_setup["node_type"] = node_type

            plugin_instance.setup()
            if plugin_instance.IMAGES:
                plugin_instance.plugin_setup["image"] = plugin_instance.IMAGES[0]
            plugin_instance.plugin_setup["pos"] = [0.0, 0.0]
            self.parent.config["plugins"].append(plugin_instance.plugin_setup)
            self.parent.redraw()
            self.parent.fit_view()
            self.parent.snapshot()

        self.plugin_table.setColumnCount(1)
        self.plugin_table.verticalHeader().setVisible(False)
        # self.plugin_table.setHorizontalHeaderItem(0, QTableWidgetItem(""))
        self.plugin_table.setHorizontalHeaderItem(0, QTableWidgetItem("Name"))
        self.plugin_table.setMinimumWidth(180)
        self.plugin_table.cellClicked.connect(plugin_select)
        self.plugin_table.doubleClicked.connect(plugin_add)

        return plugin_vbox_widget

    def plugin_info(self, plugin_name):
        node_type = None
        if " " in plugin_name:
            plugin_name, node_type = plugin_name.split(" ")

        psetup = {"type": plugin_name}
        if node_type:
            psetup["node_type"] = node_type
        self.plugins.load_plugin(plugin_name, psetup, self.parent.config)
        plugin_instance = self.plugins.plugin_instances[-1]

        infotext = plugin_instance.NAME
        infotext += f"\n\n{plugin_instance.INFO}"
        if plugin_instance.EXPERIMENTAL:
            infotext += "\n --- EXPERIMENTAL ---"

        infotext += f"\n{plugin_instance.DESCRIPTION}"
        self.pininfo.setPlainText(infotext)

    def plugin_search(self, filter_string=None, plugins=None):
        if plugins:
            self.plugins = plugins
        if not filter_string:
            filter_string = self.search_text.text()

        plugins = []
        for plugin_data in self.plugins.list(True):
            plugin_name = plugin_data["name"]
            if not filter_string or filter_string in plugin_name:
                plugins.append(plugin_data)

        self.plugin_table.setRowCount(len(plugins))
        for row, plugin_data in enumerate(plugins):
            plugin_name = plugin_data["name"]
            item = QTableWidgetItem(plugin_name)
            item.setFlags(Qt.ItemFlag.ItemIsEnabled)
            self.plugin_table.setItem(row, 0, item)

        header = self.plugin_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        self.plugin_table.resizeColumnToContents(0)

    def widget(self):
        return self.drawing_tab


class TabAxis:
    def __init__(self, parent):
        self.parent = parent
        self.config = parent.config
        self.signature = []
        self.widgets = {}

        self.tab_widget = QWidget()
        self.tab_layout = QVBoxLayout()
        self.tab_widget.setLayout(self.tab_layout)

        self.tab_axis = QScrollArea()
        self.tab_axis.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.tab_axis.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.tab_axis.setWidgetResizable(True)
        self.tab_axis.setWidget(self.tab_widget)

    def update(self, config):
        self.config = config
        if not self.widgets:
            return

        signature = []
        project = riocore.Project(copy.deepcopy(self.config), "")
        for axis in project.axis_names:
            if axis not in project.axis_dict:
                continue
            adata = project.axis_dict[axis]
            signature.append(axis)
            for jdata in adata["joints"]:
                joint = jdata["num"]
                plugin_instance = None
                plugin_setup = {}
                plugin_instance_home = None
                plugin_setup_home = {}
                for item in self.parent.scene.items():
                    if hasattr(item, "plugin_instance"):
                        if item.plugin_instance.plugin_setup["uid"] == jdata["instance"].plugin_setup["uid"]:
                            plugin_instance = item.plugin_instance
                            plugin_setup = plugin_instance.plugin_setup

                        signal = item.plugin_instance.plugin_setup.get("signals", {}).get("bit", {}).get("net", "")
                        if signal == f"joint.{joint}.home-sw-in":
                            plugin_instance_home = item.plugin_instance
                            plugin_setup_home = plugin_instance_home.plugin_setup

                if plugin_setup:
                    signature.append(joint)

                    if "joint" not in plugin_setup:
                        plugin_setup["joint"] = {}
                    joint_setup = plugin_setup["joint"]
                    position_mode = joint_setup.get("position_mode", jdata.get("mode", ""))
                    scale = joint_setup.get("SCALE_OUT", jdata.get("SCALE_OUT", ""))
                    max_velocity = joint_setup.get("max_velocity", 40.0)

                    home_sw = " --- "
                    if plugin_setup_home:
                        home_sw = plugin_instance_home.instances_name

                    text = []
                    text.append(f"Mode: {position_mode}")
                    text.append(f"Plugin-Name: {plugin_instance.instances_name}")
                    text.append(f"Home-Switch: {home_sw}")
                    text.append(f"Max-Velocity: {max_velocity * 60:0.2f} units/min")
                    max_freq = abs(max_velocity * scale)
                    if max_freq > 1500:
                        text.append(f"Max-Frequency: {max_freq / 1000:0.2f} kHz")
                    else:
                        text.append(f"Max-Frequency: {max_freq:0.2f} Hz")
                    if f"{joint}_info" in self.widgets:
                        self.widgets[f"{joint}_info"].setText("\n".join(text))

                    if "joint" not in plugin_setup:
                        plugin_setup["joint"] = {}
                    joint_setup = plugin_setup["joint"]

                    for key in ("scale", "max_velocity", "max_acceleration", "min_limit", "max_limit"):
                        if f"{joint}_{key}" in self.widgets:
                            self.widgets[f"{joint}_{key}"].update(joint_setup)
                    for key in ("home_sequence", "home", "home_offset", "home_search_vel", "home_latch_vel", "home_final_vel"):
                        if f"{joint}_{key}" in self.widgets:
                            self.widgets[f"{joint}_{key}"].update(joint_setup)

                    if plugin_setup_home:
                        signature.append("h")

        if signature != self.signature:
            self.reload(config)

    def scale_invert(self, key):
        self.widgets[key].setValue(-self.widgets[key].value())

    def home_helper(self, joint):
        dialog = QDialog()
        dialog.setWindowTitle("Home-Helper")
        dialog.setMinimumWidth(500)
        dialog.layout = QVBoxLayout()
        dialog.setLayout(dialog.layout)
        dialog_buttonBox = QDialogButtonBox(QDialogButtonBox.Cancel | QDialogButtonBox.Ok)
        dialog_buttonBox.accepted.connect(dialog.accept)
        dialog_buttonBox.rejected.connect(dialog.reject)

        self.setup = {
            "HOME_SEARCH_VEL": {"value": -30.1, "unit": "units/s"},
            "HOME_LATCH_VEL": {"value": 5.1, "unit": "units/s"},
            "HOME_FINAL_VEL": {"value": 100.1, "unit": "units/s"},
            "HOME_OFFSET": {"value": -1.1, "unit": "units"},
            "HOME": {"value": 2.1, "unit": "units"},
            "MIN_LIMIT": {"value": 0.1, "unit": "units"},
            "MAX_LIMIT": {"value": 500.1, "unit": "units"},
        }

        def update(key, value):
            self.setup[key]["value"] = value

        for key, koption in self.setup.items():
            value = self.widgets[f"{joint}_{key.lower()}"].value()
            koption["value"] = value

        vbox = QVBoxLayout()
        for key, setup in self.setup.items():
            hbox = QHBoxLayout()
            setup["label"] = QLabel(key.title())
            hbox.addWidget(setup["label"], stretch=3)
            setup["widget"] = QDoubleSpinBox()
            setup["widget"].setMinimum(-99999.0)
            setup["widget"].setMaximum(99999.0)
            setup["widget"].setDecimals(4)
            setup["widget"].setValue(float(setup["value"]))
            setup["widget"].valueChanged.connect(partial(update, key))
            hbox.addWidget(setup["widget"], stretch=5)
            hbox.addWidget(QLabel("units"), stretch=1)
            vbox.addLayout(hbox)

        self.info = QLabel("")
        self.errors = QLabel("")
        self.animation = HomeAnimation(self.setup)

        dialog.layout.addWidget(self.animation)
        dialog.layout.addWidget(self.info)
        dialog.layout.addWidget(self.errors)
        dialog.layout.addLayout(vbox)
        dialog.layout.addWidget(dialog_buttonBox)

        if dialog.exec():
            for key, koption in self.setup.items():
                value = self.setup[key]["widget"].value()
                if f"{joint}_{key.lower()}" in self.widgets:
                    self.widgets[f"{joint}_{key.lower()}"].setValue(value)

        return

    def scale_calc(self, scale_key):
        dialog = QDialog()
        dialog.setWindowTitle("Scale-Calculator")
        dialog.setMinimumWidth(400)
        dialog.scale_value = 320.0
        dialog.layout = QVBoxLayout()
        dialog.setLayout(dialog.layout)
        dialog_buttonBox = QDialogButtonBox(QDialogButtonBox.Cancel | QDialogButtonBox.Ok)
        dialog_buttonBox.accepted.connect(dialog.accept)
        dialog_buttonBox.rejected.connect(dialog.reject)

        data = {
            "motor_steps_per_rev": 200,
            "driver_microsteps": 8,
            "driver_steps_per_rev": 1600,
            "gear_teeth_in": 0,
            "gear_teeth_out": 0,
            "gear_ratio": 1.0,
            "spindle_pitch": 5.0,
        }
        defaults = {
            "motor_steps_per_rev": {
                "title": "Stepper-Motor",
                "type": int,
                "unit": "steps/rev",
                "widget": None,
            },
            "driver_microsteps": {
                "title": "Microsteps",
                "type": int,
                "unit": "steps",
                "widget": None,
            },
            "driver_steps_per_rev": {
                "title": "Driver",
                "type": float,
                "unit": "steps/rev",
                "widget": None,
            },
            "gear_teeth_in": {
                "title": "Gear-In",
                "type": int,
                "unit": "teeth",
                "widget": None,
            },
            "gear_teeth_out": {
                "title": "Gear-Out",
                "type": int,
                "unit": "teeth",
                "widget": None,
            },
            "gear_ratio": {
                "title": "Gear-Ratio",
                "type": float,
                "unit": "1:n",
                "widget": None,
            },
            "spindle_pitch": {
                "title": "Leadscrew",
                "type": float,
                "unit": "units/rev",
                "widget": None,
            },
        }

        def update_ratio(misc):
            gear_teeth_in = defaults["gear_teeth_in"]["widget"].value()
            gear_teeth_out = defaults["gear_teeth_out"]["widget"].value()
            ratio = 1.0
            if gear_teeth_in and gear_teeth_out:
                ratio = gear_teeth_out / gear_teeth_in
            defaults["gear_ratio"]["widget"].setValue(ratio)

        def update_revs(misc):
            motor_steps_per_rev = defaults["motor_steps_per_rev"]["widget"].value()
            driver_microsteps = defaults["driver_microsteps"]["widget"].value()
            driver_steps_per_rev = motor_steps_per_rev * driver_microsteps
            defaults["driver_steps_per_rev"]["widget"].setValue(driver_steps_per_rev)
            angle_label.setText(f"Full Step angle = {360.0 / motor_steps_per_rev:0.3f} deg/rev")

        def update_scale(misc):
            driver_steps_per_rev = defaults["driver_steps_per_rev"]["widget"].value()
            spindle_pitch = defaults["spindle_pitch"]["widget"].value()
            gear_ratio = defaults["gear_ratio"]["widget"].value()
            dialog.scale_value = driver_steps_per_rev * gear_ratio / spindle_pitch
            scale_label.setText(f"Joint-Scale = {dialog.scale_value:0.3f} steps/unit")

        for key, var_setup in defaults.items():
            erow = QHBoxLayout()
            erow.addWidget(QLabel(var_setup["title"]), stretch=2)
            cb = update_scale
            if key in {"motor_steps_per_rev", "driver_microsteps"}:
                cb = update_revs
            elif key in {"gear_teeth_in", "gear_teeth_out"}:
                cb = update_ratio
            var_setup["widget"] = self.parent.edit_item(data, key, var_setup, cb=cb)
            erow.addWidget(var_setup["widget"], stretch=2)
            erow.addWidget(QLabel(var_setup["unit"]), stretch=1)
            dialog.layout.addLayout(erow)

        angle_label = QLabel("Full Step angle = 1.8 deg/rev")
        dialog.layout.addWidget(angle_label)

        scale_label = QLabel("Joint-Scale = 320  steps/unit")
        dialog.layout.addWidget(scale_label)
        dialog.layout.addWidget(dialog_buttonBox)
        if dialog.exec():
            self.widgets[scale_key].setValue(dialog.scale_value)
        return

    def reload(self, config):
        self.widgets = {}
        self.signature = []
        self.config = config
        if not self.config.get("name"):
            return

        def cleanLayout(layout):
            for widget_no in range(0, layout.count()):
                if layout.itemAt(widget_no) and layout.itemAt(widget_no).widget():
                    layout.itemAt(widget_no).widget().deleteLater()
                elif layout.itemAt(widget_no) and layout.itemAt(widget_no).layout():
                    cleanLayout(layout.itemAt(widget_no).layout())
                    layout.itemAt(widget_no).layout().deleteLater()

        cleanLayout(self.tab_layout)

        def jedit(plugin_instance):
            self.parent.scene.parent.gui_plugins.edit_plugin(plugin_instance, None)
            self.parent.scene.parent.redraw()
            self.parent.scene.parent.snapshot()

        def scale_calc(plugin_instance):
            self.parent.scene.parent.gui_plugins.edit_plugin(plugin_instance, None)
            self.parent.scene.parent.redraw()
            self.parent.scene.parent.snapshot()

        project = riocore.Project(copy.deepcopy(self.config), "")
        for axis in project.axis_names:
            if axis not in project.axis_dict:
                continue
            adata = project.axis_dict[axis]
            self.signature.append(axis)
            axis_box = QHBoxLayout()
            self.tab_layout.addLayout(axis_box, stretch=0)

            axis_box_axis = QVBoxLayout()
            axis_box.addLayout(axis_box_axis, stretch=0)

            axis_box_joints = QVBoxLayout()
            axis_box.addLayout(axis_box_joints, stretch=0)

            label = QLabel(f"{axis} ")
            label.setStyleSheet("QLabel{font-size:32px;}")
            axis_box_axis.addWidget(label, stretch=0)

            for jdata in adata["joints"]:
                joint = jdata["num"]
                self.signature.append(joint)
                plugin_instance = None
                plugin_setup = {}
                plugin_instance_home = None
                plugin_setup_home = {}
                for item in self.parent.scene.items():
                    if hasattr(item, "plugin_instance"):
                        if item.plugin_instance.plugin_setup["uid"] == jdata["instance"].plugin_setup["uid"]:
                            plugin_instance = item.plugin_instance
                            plugin_setup = plugin_instance.plugin_setup

                        signal = item.plugin_instance.plugin_setup.get("signals", {}).get("bit", {}).get("net", "")
                        if signal == f"joint.{joint}.home-sw-in":
                            plugin_instance_home = item.plugin_instance
                            plugin_setup_home = plugin_instance_home.plugin_setup

                if plugin_setup:
                    if "joint" not in plugin_setup:
                        plugin_setup["joint"] = {}
                    joint_setup = plugin_setup["joint"]

                    row = QHBoxLayout()
                    label = QLabel(f" Joint-{joint} ")
                    label.setStyleSheet("QLabel{font-size:27px;}")
                    row.addWidget(label, stretch=0)

                    info = QLabel("---")
                    self.widgets[f"{joint}_info"] = info
                    row.addWidget(info, stretch=1)

                    joint_edits = QVBoxLayout()
                    for key in ("scale", "max_velocity", "max_acceleration", "min_limit", "max_limit"):
                        options = riocore.halpins.JOINT_OPTIONS[key]
                        unit = options.get("unit", "")
                        dkey = key.upper()
                        if key == "scale":
                            dkey = "SCALE_OUT"
                        default = riocore.generator.LinuxCNC.LinuxCNC.JOINT_DEFAULTS.get(dkey)
                        if default:
                            options["default"] = default
                        widget = self.parent.edit_item(joint_setup, key, options)
                        self.widgets[f"{joint}_{key}"] = widget
                        ulabel = QLabel(unit)
                        ulabel.setStyleSheet("QLabel{font-size:12px;}")
                        erow = QHBoxLayout()
                        erow.addWidget(QLabel(key.title()), stretch=2)
                        erow.addWidget(widget, stretch=4)

                        if key == "scale":
                            text = "INV."
                            button = QPushButton(text)
                            width = button.fontMetrics().boundingRect(text).width()
                            button.setMinimumWidth(width)
                            button.clicked.connect(partial(self.scale_invert, f"{joint}_{key}"))
                            erow.addWidget(button, stretch=1)
                        else:
                            erow.addWidget(ulabel, stretch=1)

                        joint_edits.addLayout(erow)

                    brow = QHBoxLayout()
                    button = QPushButton("joint-plugin")
                    button.clicked.connect(partial(jedit, plugin_instance))
                    brow.addWidget(button)
                    button = QPushButton("scale-calc")
                    button.clicked.connect(partial(self.scale_calc, f"{joint}_scale"))
                    brow.addWidget(button)
                    joint_edits.addLayout(brow)

                    row.addLayout(joint_edits, stretch=2)

                    home_options = {}
                    home_edits = QVBoxLayout()
                    for key in ("home_sequence", "home", "home_offset", "home_search_vel", "home_latch_vel", "home_final_vel"):
                        options = riocore.halpins.JOINT_OPTIONS[key]
                        home_options[key.upper()] = options
                        unit = options.get("unit", "")
                        default = riocore.generator.LinuxCNC.LinuxCNC.JOINT_DEFAULTS.get(key.upper())
                        if default:
                            options["default"] = default
                        widget = self.parent.edit_item(joint_setup, key, riocore.halpins.JOINT_OPTIONS[key])
                        self.widgets[f"{joint}_{key}"] = widget
                        ulabel = QLabel(unit)
                        ulabel.setStyleSheet("QLabel{font-size:12px;}")
                        erow = QHBoxLayout()
                        erow.addWidget(QLabel(key.title()), stretch=2)
                        erow.addWidget(widget, stretch=4)
                        erow.addWidget(ulabel, stretch=1)
                        home_edits.addLayout(erow)
                    button = QPushButton("home-plugin")
                    if plugin_setup_home:
                        self.signature.append("h")
                        button.clicked.connect(partial(jedit, plugin_instance_home))
                    else:
                        button.setEnabled(False)
                    brow = QHBoxLayout()
                    brow.addWidget(button)
                    button = QPushButton("home-helper")
                    button.clicked.connect(partial(self.home_helper, joint))
                    brow.addWidget(button)
                    home_edits.addLayout(brow)
                    row.addLayout(home_edits, stretch=2)

                    axis_box_joints.addLayout(row)

    def widget(self):
        return self.tab_axis


class TabOptions:
    def __init__(self, parent):
        self.parent = parent
        self.config = parent.config
        self.update_flag = False
        self.ini_items = {}
        self.items = {}
        self.help_img1 = None
        self.help_img2 = None

        self.tab_misc = QWidget()
        self.layout_misc = QVBoxLayout()
        self.tab_misc.setLayout(self.layout_misc)

        self.tab_linuxcnc = QWidget()
        self.layout_linuxcnc = QVBoxLayout()
        self.tab_linuxcnc.setLayout(self.layout_linuxcnc)

        self.tab_ini = QWidget()
        self.layout_ini = QVBoxLayout()
        self.tab_ini.setLayout(self.layout_ini)

        self.tab_hal = QWidget()
        self.layout_hal = QVBoxLayout()
        self.tab_hal.setLayout(self.layout_hal)

        tab_axis_widget = QWidget()
        self.layout_axis = QVBoxLayout()
        tab_axis_widget.setLayout(self.layout_axis)

        self.tab_widget = QTabWidget()
        self.tab_widget.addTab(self.tab_misc, "Misc")
        self.tab_widget.addTab(self.tab_linuxcnc, "LinuxCNC")
        self.tab_widget.addTab(self.tab_ini, "INI-Defaults")
        self.tab_widget.addTab(self.tab_hal, "HAL-Signals")

        self.treeview = QTreeView()
        self.model = QStandardItemModel()
        self.model.setHorizontalHeaderLabels(["Name", "Value"])
        self.treeview.setModel(self.model)
        self.treeview.setUniformRowHeights(True)
        self.layout_ini.addWidget(self.treeview)

        self.phal_table = QTableWidget()
        self.phal_table.setColumnCount(4)
        self.phal_table.setHorizontalHeaderItem(0, QTableWidgetItem("Plugin"))
        self.phal_table.setHorizontalHeaderItem(1, QTableWidgetItem("Signal"))
        self.phal_table.setHorizontalHeaderItem(2, QTableWidgetItem("Target"))
        self.phal_table.setHorizontalHeaderItem(3, QTableWidgetItem("Type"))
        self.layout_hal.addWidget(self.phal_table)

        self.hal_table = QTableWidget()
        self.hal_table.setColumnCount(3)
        self.hal_table.setHorizontalHeaderItem(0, QTableWidgetItem("Source"))
        self.hal_table.setHorizontalHeaderItem(1, QTableWidgetItem("Target"))
        self.hal_table.setHorizontalHeaderItem(2, QTableWidgetItem("Type"))
        self.layout_hal.addWidget(self.hal_table)

    def update(self, config):
        self.update_flag = True

        self.config = config
        if "linuxcnc" not in self.config:
            self.config["linuxcnc"] = {}
        for key, data in self.items.items():
            if "item" in data:
                data["item"].update(self.config["linuxcnc"])
            if "item2" in data:
                data["item2"].update(self.config)
            if "item3" in data:
                data["item3"].update()

        # ini
        self.load_tree_linuxcnc_ini(self.model)
        self.treeview.setColumnWidth(0, 280)

        # hal
        row = 0
        self.hal_table.setRowCount(1 + len(self.config["linuxcnc"].get("net", [])) + len(self.config["linuxcnc"].get("setp", {}).keys()))
        for entry in self.config["linuxcnc"].get("net", []):
            source = entry.get("source", "")
            target = entry.get("target", "")
            self.hal_table.setItem(row, 0, QTableWidgetItem(source))
            self.hal_table.setItem(row, 1, QTableWidgetItem(target))
            item = QTableWidgetItem("net")
            item.setFlags(Qt.ItemFlag.ItemIsEnabled)
            self.hal_table.setItem(row, 2, item)
            row += 1

        for pin, value in self.config["linuxcnc"].get("setp", {}).items():
            self.hal_table.setItem(row, 0, QTableWidgetItem(pin))
            self.hal_table.setItem(row, 1, QTableWidgetItem(str(value)))
            item = QTableWidgetItem("setp")
            item.setFlags(Qt.ItemFlag.ItemIsEnabled)
            self.hal_table.setItem(row, 2, item)
            row += 1

        self.hal_table.setItem(row, 0, QTableWidgetItem(""))
        self.hal_table.setItem(row, 1, QTableWidgetItem(""))
        self.hal_table.setItem(row, 2, QTableWidgetItem(""))
        self.hal_table.resizeColumnToContents(2)
        self.hal_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.hal_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.hal_table.itemChanged.connect(self.table_updated)

        row = 0
        for sitem in self.parent.scene.items():
            if hasattr(sitem, "plugin_instance"):
                plugin_config = sitem.plugin_instance.plugin_setup
                uid = sitem.plugin_instance.plugin_setup["uid"]
                for signal, sconf in plugin_config.get("signals", {}).items():
                    self.phal_table.setRowCount(row + 1)
                    net = sconf.get("net")
                    setp = sconf.get("setp")
                    item = QTableWidgetItem(uid)
                    item.setFlags(Qt.ItemFlag.ItemIsEnabled)
                    self.phal_table.setItem(row, 0, item)
                    item = QTableWidgetItem(signal)
                    item.setFlags(Qt.ItemFlag.ItemIsEnabled)
                    self.phal_table.setItem(row, 1, item)
                    if net:
                        self.phal_table.setItem(row, 2, QTableWidgetItem(str(net)))
                        item = QTableWidgetItem("net")
                    elif setp:
                        self.phal_table.setItem(row, 2, QTableWidgetItem(str(setp)))
                        item = QTableWidgetItem("setp")
                    else:
                        item = QTableWidgetItem("")
                    item.setFlags(Qt.ItemFlag.ItemIsEnabled)
                    self.phal_table.setItem(row, 3, item)
                    row += 1

        self.phal_table.resizeColumnToContents(0)
        self.phal_table.resizeColumnToContents(1)
        self.phal_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.phal_table.resizeColumnToContents(3)
        self.phal_table.itemChanged.connect(self.table_updated)

        # Misc
        machinetype = self.config["linuxcnc"].get("machinetype", "mill")
        image_path = os.path.join(riocore_path, "files", "images", f"{machinetype}.png")
        if self.help_img1 is not None:
            if os.path.isfile(image_path):
                pixmap = QPixmap(image_path)
            else:
                pixmap = QPixmap(None)
            self.help_img1.setPixmap(pixmap)

        gui = self.config["linuxcnc"].get("gui", "axis")
        image_path = os.path.join(riocore_path, "files", "images", f"{gui}.png")
        if self.help_img2 is not None:
            if os.path.isfile(image_path):
                pixmap = QPixmap(image_path)
            else:
                pixmap = QPixmap(None)
            self.help_img2.setPixmap(pixmap)

        self.update_flag = False

    def get_path(self, path):
        if os.path.exists(path):
            return path
        elif os.path.exists(os.path.join(riocore_path, path)):
            return os.path.join(riocore_path, path)
        elif os.path.exists(os.path.join(riocore_path, "riocore", path)):
            return os.path.join(riocore_path, path)
        riocore.log(f"can not find path: {path}")
        # exit(1)

    def load_tree_linuxcnc_ini(self, parent_tree):
        if "ini" not in self.config["linuxcnc"]:
            self.config["linuxcnc"]["ini"] = {}
        ini_config = self.config["linuxcnc"]["ini"]
        ini_data = riocore.generator.LinuxCNC.LinuxCNC.ini_defaults(self.config)

        if self.ini_items:
            for section, section_data in ini_data.items():
                if section not in ini_config:
                    ini_config[section] = {}
                section_config = ini_config[section]
                for key, value in section_data.items():
                    if value is not None and not isinstance(value, list):
                        if f"{section}_{key}" not in self.ini_items:
                            continue
                        self.ini_items[f"{section}_{key}"].update(section_config)

            return

        tree_lcncini = parent_tree
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
            lcncsec_view = tree_lcncini.item(tree_lcncini.rowCount() - 1)
            for key, value in section_data.items():
                if value is not None and not isinstance(value, list):
                    var_setup = {"type": type(value), "default": value}
                    if section == "DISPLAY" and key == "POSITION_OFFSET":
                        var_setup["type"] = "select"
                        var_setup["options"] = ["RELATIVE", "MACHINE"]
                    elif section == "DISPLAY" and key == "POSITION_FEEDBACK":
                        var_setup["type"] = "select"
                        var_setup["options"] = ["COMMANDED", "ACTUAL"]
                    elif section == "HAL" and key == "TWOPASS":
                        var_setup["type"] = "select"
                        var_setup["options"] = ["ON", "OFF"]
                    elif section == "DISPLAY" and key == "PYVCP_POSITION":
                        var_setup["type"] = "select"
                        var_setup["options"] = ["RIGHT", "BOTTOM"]
                    elif section == "TRAJ" and key == "LINEAR_UNITS":
                        var_setup["type"] = "select"
                        var_setup["options"] = ["in", "inch", "imperial", "metric", "mm"]
                    elif section == "TRAJ" and key == "ANGULAR_UNITS":
                        var_setup["type"] = "select"
                        var_setup["options"] = ["deg", "degree", "rad", "radian", "grad", "gon"]
                    elif section == "MQTT" and key == "DRYRUN":
                        var_setup["type"] = "select"
                        var_setup["options"] = ["", "--dryrun"]

                    if section in riocore.halpins.INI_HELPTEXT and key in riocore.halpins.INI_HELPTEXT[section]:
                        var_setup["tooltip"] = riocore.halpins.INI_HELPTEXT[section][key]

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
                    widget = self.parent.edit_item(section_config, key, var_setup, cb=self.updated)
                    self.treeview.setIndexWidget(aitem.index(), widget)
                    self.ini_items[f"{section}_{key}"] = widget
        self.treeview.expandAll()

    def load(self):
        boards_path = self.get_path("boards")
        self.boards = [""]
        for path in sorted(glob.glob(os.path.join(boards_path, "*", "board.json"))):
            self.boards.append(path.split(os.sep)[-2].replace(".json", ""))
        for path in sorted(glob.glob(os.path.join(boards_path, "*.json"))):
            self.boards.append(path.split(os.sep)[-1].replace(".json", ""))

        self.interfaces = []
        for path in sorted(glob.glob(os.path.join(riocore_path, "interfaces", "*"))):
            self.interfaces.append(path.split(os.sep)[-1])

        toolchain = self.parent.board.get("toolchain")
        toolchains = self.parent.board.get("toolchains", [toolchain])

        options = {
            "name": {"type": str},
            "description": {"type": str},
            "boardcfg": {"type": "select", "options": self.boards},
        }
        options.update(
            {
                "toolchain": {"type": "select", "options": toolchains, "default": toolchain},
                "protocol": {"type": "select", "options": self.interfaces, "default": "SPI"},
            }
        )
        for key, var_setup in options.items():
            row = QHBoxLayout()
            self.layout_misc.addLayout(row)
            row.addWidget(QLabel(key.title()), stretch=1)
            item = self.parent.edit_item(self.config, key, var_setup, cb=self.updated)
            row.addWidget(item, stretch=1)
            self.items[key] = {"item2": item}
        self.layout_misc.addStretch()

        if "linuxcnc" not in self.config:
            self.config["linuxcnc"] = {}

        hbox = QHBoxLayout()
        self.layout_linuxcnc.addLayout(hbox)

        vbox = QVBoxLayout()
        hbox.addLayout(vbox, stretch=3)

        for key, var_setup in {
            "num_axis": {"type": int, "min": 0, "max": 9, "default": 3, "help_text": "number of axis"},
            "machinetype": {"type": "select", "options": ["mill", "lathe", "corexy", "ldelta", "rdelta", "scara", "puma", "melfa"], "help_text": "type of the machine"},
            "toolchange": {"type": "select", "options": ["manual", "auto"], "default": "manual", "help_text": "type of the toolchanger"},
            "gui": {
                "type": "select",
                "options": ["axis", "qtdragon", "qtdragon_hd", "tklinuxcnc", "touchy", "probe_basic", "probe_basic_lathe", "gmoccapy", "gscreen", "tnc"],
                "default": "axis",
                "help_text": "linuxcnc gui to use",
            },
            "vcp_mode": {"type": "select", "options": ["ALL", "CONFIGURED", "NONE"], "default": "ALL", "help_text": "pyvcp gui generate mode"},
            "vcp_pos": {"type": "select", "options": ["RIGHT", "BOTTOM", "TAB"], "default": "RIGHT", "help_text": "position of the vcp gui for extra controls"},
            "vcp_type": {"type": "select", "options": ["auto", "pyvcp", "qtvcp", "gladevcp"], "default": "auto", "help_text": "vcp type, depends on the gui"},
            "embed_vismach": {"type": "select", "options": ["", "fanuc_200f"], "default": ""},
            "debug_info": {"type": bool, "help_text": "Displays some debug infos in VCP", "default": False},
            "simulation": {"type": bool, "help_text": "Enables the board simulator / no hardware needed", "default": False},
        }.items():
            row = QHBoxLayout()
            vbox.addLayout(row)
            label = QLabel(key.title())
            if "help_text" in var_setup:
                label.setToolTip(var_setup["help_text"])
            row.addWidget(label)
            item = self.parent.edit_item(self.config["linuxcnc"], key, var_setup, cb=self.updated)
            row.addWidget(item)
            self.items[key] = {"item": item}
        vbox.addStretch()

        vbox2 = QVBoxLayout()
        hbox.addLayout(vbox2, stretch=1)
        self.help_img1 = QLabel()
        vbox2.addWidget(self.help_img1)
        self.help_img2 = QLabel()
        vbox2.addWidget(self.help_img2)
        vbox2.addStretch()

    def table_updated(self):
        if self.update_flag:
            return

        # nets/setps
        nrows = self.hal_table.rowCount()
        self.config["linuxcnc"]["net"] = []
        self.config["linuxcnc"]["setp"] = {}
        for row in range(0, nrows):
            if self.hal_table.item(row, 0) and self.hal_table.item(row, 1):
                source = str(self.hal_table.item(row, 0).text())
                target = str(self.hal_table.item(row, 1).text())
                if source or target:
                    if target.replace(".", "").isnumeric():
                        self.config["linuxcnc"]["setp"][source] = target
                    else:
                        self.config["linuxcnc"]["net"].append(
                            {
                                "source": source,
                                "target": target,
                            }
                        )
        # plugin signals
        nrows = self.phal_table.rowCount()
        signals = {}
        for row in range(0, nrows):
            if self.phal_table.item(row, 1) and self.phal_table.item(row, 2):
                uid = str(self.phal_table.item(row, 0).text())
                source = str(self.phal_table.item(row, 1).text())
                target = str(self.phal_table.item(row, 2).text())
                if target:
                    if uid not in signals:
                        signals[uid] = {}
                    signals[uid][source] = target
        for item in self.parent.scene.items():
            if hasattr(item, "plugin_instance"):
                plugin_config = item.plugin_instance.plugin_setup
                uid = item.plugin_instance.plugin_setup["uid"]
                if uid in signals:
                    for source, target in signals[uid].items():
                        if "signals" not in plugin_config:
                            plugin_config["signals"] = {}
                        if target.replace(".", "").isnumeric():
                            plugin_config["signals"][source] = {"setp": target}
                        else:
                            plugin_config["signals"][source] = {"net": target}

        self.updated()

    def updated(self, tmp=None):
        self.parent.redraw()
        self.parent.cfg_check()
        self.update(self.config)

    def widget(self):
        return self.tab_widget
