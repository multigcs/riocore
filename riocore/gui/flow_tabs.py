import copy
import difflib
import json
import os
import subprocess
from functools import partial

from PyQt5.QtCore import QMimeData, QTimer, Qt, QSortFilterProxyModel
from PyQt5.QtGui import QColor, QDrag, QPixmap, QStandardItemModel, QTextCursor
from PyQt5.QtWidgets import (
    QCompleter,
    QComboBox,
    QMessageBox,
    QDialog,
    QDialogButtonBox,
    QDoubleSpinBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QPlainTextEdit,
    QPushButton,
    QScrollArea,
    QSpacerItem,
    QSplitter,
    QTabWidget,
    QTableWidget,
    QTableWidgetItem,
    QTreeView,
    QVBoxLayout,
    QWidget,
    QWidgetItem,
)

import riocore
from riocore.gui.home_helper import HomeAnimation
from riocore.gui.widgets import MyStandardItem

riocore_path = os.path.dirname(riocore.__file__)


def cleanLayout(layout):
    for i in reversed(range(layout.count())):
        item = layout.itemAt(i)
        if isinstance(item, QWidgetItem):
            item.widget().close()
        elif isinstance(item, QSpacerItem):
            pass
        else:
            cleanLayout(item.layout())
        layout.removeItem(item)


class DragLabel(QLabel):
    def __init__(self, title):
        super().__init__(title)
        self.title = title

    def mouseMoveEvent(self, e):
        if e.buttons() == Qt.LeftButton:
            drag = QDrag(self)
            mime = QMimeData()
            jdata = json.dumps({"type": "plugin", "name": self.title})
            mime.setData("text/json", jdata.encode())
            drag.setMimeData(mime)
            drag.exec_(Qt.MoveAction)


class TabBuilder:
    def __init__(self, parent):
        self.parent = parent
        self.block = False

        self.builder_tab = QWidget()
        builder_tab_layout = QHBoxLayout()
        self.builder_tab.setLayout(builder_tab_layout)

        self.left = QVBoxLayout()
        self.right = QVBoxLayout()

        builder_tab_layout.addLayout(self.left, stretch=1)
        builder_tab_layout.addLayout(self.right, stretch=4)

        self.compile_sub = {}
        self.output = {}

        self.timer = QTimer()
        self.timer.timeout.connect(self.runTimer)
        self.timer.start(300)

    def runTimer(self):
        running = False
        if "generator" in self.compile_sub and os.path.exists("/tmp/buildlog"):
            logdata = open("/tmp/buildlog").read()
            if self.output["generator"].verticalScrollBar().maximum() == self.output["generator"].verticalScrollBar().value():
                self.output["generator"].setPlainText(logdata)
                self.output["generator"].verticalScrollBar().setValue(self.output["generator"].verticalScrollBar().maximum())
            if self.compile_sub["generator"].poll() is not None:
                del self.compile_sub["generator"]
                self.block = False
                self.output["generator"].appendPlainText("...done")
                print("...done")
            else:
                running = True

        for item in self.parent.scene.items():
            if hasattr(item, "plugin_instance"):
                plugin_instance = item.plugin_instance
                if not plugin_instance.BUILDER:
                    continue
                if plugin_instance.instances_name in self.compile_sub and os.path.exists(f"/tmp/buildlog-{plugin_instance.instances_name}"):
                    logdata = open(f"/tmp/buildlog-{plugin_instance.instances_name}").read()
                    if self.output[plugin_instance.instances_name].verticalScrollBar().maximum() == self.output[plugin_instance.instances_name].verticalScrollBar().value():
                        self.output[plugin_instance.instances_name].setPlainText(logdata)
                        self.output[plugin_instance.instances_name].verticalScrollBar().setValue(self.output[plugin_instance.instances_name].verticalScrollBar().maximum())
                    if self.compile_sub[plugin_instance.instances_name].poll() is not None:
                        del self.compile_sub[plugin_instance.instances_name]
                        self.block = False
                        self.output[plugin_instance.instances_name].appendPlainText("...done")
                        print("...done")
                    else:
                        running = True
        if running:
            self.parent.tabwidget.tabBar().setTabTextColor(4, QColor(255, 0, 0))
            self.block = True
        else:
            self.parent.tabwidget.tabBar().setTabTextColor(4, QColor(0, 0, 0))
            self.block = False

    def generator_run(self, options=None):
        if "generator" in self.compile_sub:
            print("wait to finish already running command")
            return

        generator_path = os.path.join(os.path.dirname(riocore_path), "bin/rio-generator")
        cmd = f"{generator_path} {options or ''} {self.parent.config_file}"
        self.output["generator"].setPlainText(f"running cmd; {cmd}...")
        print(f"running cmd: {cmd}...")
        self.compile_sub["generator"] = subprocess.Popen(f"{cmd} > /tmp/buildlog 2>&1", shell=True, close_fds=True)

    def builder_run(self, plugin_instance, command):
        if plugin_instance.instances_name in self.compile_sub:
            print("wait to finish already running command")
            return
        if not self.parent.save_check():
            # cancel pressed
            return

        cmd = plugin_instance.builder(self.parent.config, command)
        if cmd is None:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setText("Error")
            msg.setWindowTitle("Error")
            msg.setInformativeText("can not run command, please press\n\n'Generate files'\n\nfirst")
            msg.exec_()
            return

        self.output[plugin_instance.instances_name].setPlainText(f"running cmd; {cmd}...")
        print(f"running cmd; {cmd}...")
        self.compile_sub[plugin_instance.instances_name] = subprocess.Popen(f"{cmd} > /tmp/buildlog-{plugin_instance.instances_name} 2>&1", shell=True, close_fds=True)

    def update_right(self):
        cleanLayout(self.right)
        self.output = {}

        self.output["generator"] = QPlainTextEdit("--- generator ---")
        self.right.addWidget(self.output["generator"], stretch=1)

        for item in self.parent.scene.items():
            if hasattr(item, "plugin_instance"):
                plugin_instance = item.plugin_instance
                if not plugin_instance.BUILDER:
                    continue

                self.output[plugin_instance.instances_name] = QPlainTextEdit(f"--- {plugin_instance.instances_name} ---")
                self.right.addWidget(self.output[plugin_instance.instances_name], stretch=1)

        self.right.addStretch()

    def update_left(self):
        cleanLayout(self.left)

        button = QPushButton("Generate files")
        button.clicked.connect(self.generator_run)
        self.left.addWidget(button)

        for item in self.parent.scene.items():
            if hasattr(item, "plugin_instance"):
                plugin_instance = item.plugin_instance
                if not plugin_instance.BUILDER:
                    continue

                vbox = QVBoxLayout()
                self.left.addLayout(vbox)
                vbox.addWidget(QLabel(""))
                vbox.addWidget(QLabel(plugin_instance.title))

                for command in plugin_instance.BUILDER:
                    button = QPushButton(command)
                    button.clicked.connect(partial(self.builder_run, plugin_instance, command))
                    vbox.addWidget(button)

        self.left.addStretch()

    def update(self):
        if self.block:
            print("wait to finish already running command")
            return

        self.update_left()
        self.update_right()

    def widget(self):
        return self.builder_tab


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

        self.pluginlist = {}

        def plugin_select(idx):
            self.plugin_name_selected = self.pluginlist[idx]
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

            unum = 0
            while f"{self.plugin_name_selected}{unum}" in self.parent.plugin_uids:
                unum += 1
            self.plugins.load_plugin(unum, psetup, self.parent.config)
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
        self.plugin_table.setMinimumWidth(200)
        self.plugin_table.cellClicked.connect(plugin_select)
        self.plugin_table.doubleClicked.connect(plugin_add)

        return plugin_vbox_widget

    def plugin_info(self, plugin_name):
        node_type = None
        if plugin_name and plugin_name[0] == "-":
            return
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

            if not filter_string:
                plugins.append(plugin_data)
                continue
            filter_string = filter_string.lower()

            if filter_string in plugin_name.lower() or filter_string in plugin_data["description"].lower() or filter_string in plugin_data["info"].lower() or filter_string in plugin_data["keywords"].lower():
                plugins.append(plugin_data)

        ptypes = set()
        for plugin_data in plugins:
            ptypes.add(plugin_data["ptype"])

        row = 0
        for ptype in sorted(ptypes):
            self.plugin_table.setRowCount(row + 1)
            item = QTableWidgetItem()
            item.setFlags(Qt.ItemFlag.ItemIsEnabled)
            self.plugin_table.setItem(row, 0, item)

            label = QLabel(ptype.title())
            label.setStyleSheet("QLabel { background-color: gray; color: white; font-size:14px; qproperty-alignment: AlignCenter;}")

            self.plugin_table.setCellWidget(row, 0, label)
            row += 1
            for plugin_data in plugins:
                if plugin_data["ptype"] != ptype:
                    continue
                self.plugin_table.setRowCount(row + 1)
                plugin_name = plugin_data["name"]
                item = QTableWidgetItem()
                item.setFlags(Qt.ItemFlag.ItemIsEnabled)

                label = DragLabel(plugin_name)
                self.pluginlist[row] = plugin_name
                self.plugin_table.setCellWidget(row, 0, label)

                self.plugin_table.setItem(row, 0, item)
                row += 1

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
        self.project = project
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
                plugin_instance_encoder = jdata.get("feedback_instance")
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

                    encoder = " --- "
                    if plugin_instance_encoder:
                        encoder = plugin_instance_encoder.instances_name

                    text = []
                    text.append(f"Mode: {position_mode}")
                    text.append(f"Plugin-Name: {plugin_instance.instances_name}")
                    text.append(f"Home-Switch: {home_sw}")
                    text.append(f"Feedback: {encoder}")
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

                    for key in (
                        "scale_in",
                        "scale_out",
                        "max_velocity",
                        "max_acceleration",
                        "min_limit",
                        "max_limit",
                        "home_sequence",
                        "home",
                        "home_offset",
                        "home_search_vel",
                        "home_latch_vel",
                        "home_final_vel",
                    ):
                        if f"{joint}_{key}" in self.widgets:
                            self.widgets[f"{joint}_{key}"].update()

                    if plugin_instance_home:
                        signature.append("h")
                    else:
                        self.signature.append("sh")

                    if plugin_instance_encoder:
                        signature.append("e")

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

    def reload(self, config):
        self.widgets = {}
        self.signature = []
        self.config = config
        if not self.config.get("name"):
            return

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
                plugin_instance_encoder = jdata.get("feedback_instance")
                plugin_setup_encoder = {}
                for item in self.parent.scene.items():
                    if hasattr(item, "plugin_instance"):
                        if item.plugin_instance.plugin_setup["uid"] == jdata["instance"].plugin_setup["uid"]:
                            plugin_instance = item.plugin_instance
                            plugin_setup = plugin_instance.plugin_setup

                        if plugin_instance_encoder and item.plugin_instance.plugin_setup["uid"] == plugin_instance_encoder.plugin_setup["uid"]:
                            plugin_instance_encoder = item.plugin_instance
                            feedback_signal = jdata.get("feedback_signal")
                            if "signals" not in plugin_instance_encoder.plugin_setup:
                                plugin_instance_encoder.plugin_setup["signals"] = {}
                            if feedback_signal not in plugin_instance_encoder.plugin_setup["signals"]:
                                plugin_instance_encoder.plugin_setup["signals"][feedback_signal] = {}
                            plugin_setup_encoder = plugin_instance_encoder.plugin_setup["signals"][feedback_signal]
                        signal = item.plugin_instance.plugin_setup.get("signals", {}).get("bit", {}).get("net", "")
                        if signal == f"joint.{joint}.home-sw-in":
                            plugin_instance_home = item.plugin_instance

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

                    keys = ["scale_out", "max_velocity", "max_acceleration", "min_limit", "max_limit"]
                    if plugin_instance_encoder:
                        keys = ["scale_in"] + keys

                    for key in keys:
                        options = riocore.halpins.JOINT_OPTIONS[{"scale_in": "scale", "scale_out": "scale"}.get(key, key)]
                        unit = options.get("unit", "")
                        dkey = key.upper()
                        default = riocore.generator.LinuxCNC.LinuxCNC.JOINT_DEFAULTS.get(dkey)
                        if default:
                            options["default"] = default

                        ekey = key
                        if ekey == "scale_in":
                            ekey = "scale"
                            widget = self.parent.edit_item(plugin_setup_encoder, ekey, options)
                        else:
                            if ekey == "scale_out":
                                ekey = "scale"
                            widget = self.parent.edit_item(joint_setup, ekey, options)

                        self.widgets[f"{joint}_{key}"] = widget
                        ulabel = QLabel(unit)
                        ulabel.setStyleSheet("QLabel{font-size:12px;}")
                        erow = QHBoxLayout()
                        erow.addWidget(QLabel(key.title()), stretch=2)
                        erow.addWidget(widget, stretch=4)

                        if key in {"scale_in", "scale_out"}:
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

                    if plugin_instance_encoder:
                        button = QPushButton("encoder-plugin")
                        button.clicked.connect(partial(jedit, plugin_instance_encoder))
                        brow.addWidget(button)

                    button = QPushButton("scale-calc")
                    button.clicked.connect(partial(self.scale_calc, f"{joint}_scale_out"))
                    brow.addWidget(button)
                    joint_edits.addLayout(brow)

                    row.addLayout(joint_edits, stretch=2)

                    home_options = {}
                    home_edits = QVBoxLayout()
                    for key in ("home_sequence", "home", "home_offset", "home_search_vel", "home_latch_vel", "home_final_vel"):
                        options = riocore.halpins.JOINT_OPTIONS[key]
                        home_options[key.upper()] = options
                        unit = options.get("unit", "")

                        if key.upper() in jdata:
                            options["default"] = jdata.get(key.upper())
                        else:
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
                    if plugin_instance_home:
                        button = QPushButton("home-plugin")
                        self.signature.append("h")
                        button.clicked.connect(partial(jedit, plugin_instance_home))
                    else:
                        button = QPushButton("select input")
                        self.signature.append("sh")
                        button.clicked.connect(partial(self.select_home, joint))

                    brow = QHBoxLayout()
                    brow.addWidget(button)
                    button = QPushButton("home-helper")
                    button.clicked.connect(partial(self.home_helper, joint))
                    brow.addWidget(button)
                    home_edits.addLayout(brow)
                    row.addLayout(home_edits, stretch=2)

                    if plugin_instance_encoder:
                        self.signature.append("e")

                    axis_box_joints.addLayout(row)

    def select_home(self, jnum):
        dialog = QDialog()
        dialog.setWindowTitle(f"select home plugin for joint {jnum}")
        dialog.buttonBox = QDialogButtonBox(QDialogButtonBox.Ok)
        dialog.buttonBox.accepted.connect(dialog.accept)

        dialog.layout = QVBoxLayout()
        halpin = QComboBox()
        halpin.addItem("")
        plugin_instances = {}

        for item in self.parent.scene.items():
            if hasattr(item, "plugin_instance"):
                if "bit" in item.plugin_instance.SIGNALS and item.plugin_instance.SIGNALS["bit"].get("direction") == "input":
                    if item.plugin_instance.plugin_setup.get("signals", {}).get("bit", {}).get("net"):
                        continue
                    title = f"{item.plugin_instance.title}"
                    halpin.addItem(title)
                    plugin_instances[title] = item.plugin_instance

        dialog.layout.addWidget(halpin)
        dialog.layout.addWidget(dialog.buttonBox)
        dialog.setLayout(dialog.layout)

        if dialog.exec():
            title = halpin.currentText()
            if title:
                plugin_setup = plugin_instances[title].plugin_setup
                if "signals" not in plugin_setup:
                    plugin_setup["signals"] = {}
                if "bit" not in plugin_setup["signals"]:
                    plugin_setup["signals"]["bit"] = {}
                plugin_setup["signals"]["bit"]["net"] = f"joint.{jnum}.home-sw-in"
                self.parent.scene.parent.redraw()
                self.parent.scene.parent.snapshot()

    def widget(self):
        return self.tab_axis


class SearchComboBox(QComboBox):
    def __init__(self, cb):
        super().__init__()
        self.cb = cb
        self.setEditable(True)
        self.setInsertPolicy(QComboBox.NoInsert)
        self.pFilterModel = QSortFilterProxyModel(self)
        self.pFilterModel.setFilterCaseSensitivity(Qt.CaseInsensitive)
        self.pFilterModel.setSourceModel(self.model())
        self.completer = QCompleter(self.pFilterModel, self)
        self.completer.setCompletionMode(QCompleter.UnfilteredPopupCompletion)
        self.setCompleter(self.completer)
        self.lineEdit().textEdited[str].connect(self.pFilterModel.setFilterFixedString)
        self.completer.activated.connect(self.on_completer_activated)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Return:
            self.cb()
        else:
            QComboBox.keyPressEvent(self, event)

    def on_completer_activated(self, text):
        if text:
            index = self.findText(text)
            self.setCurrentIndex(index)
            self.activated[str].emit(self.itemText(index))


class TabJson:
    def __init__(self, parent=None, diff_only=True, line_numbers=True):
        self.parent = parent
        self.jsondiff = QPlainTextEdit()
        self.jsondiff.clear()
        self.jsondiff.insertPlainText("...")
        self.diff_only = diff_only
        self.line_numbers = line_numbers
        self.found_diffs = False

    def widget(self):
        return self.jsondiff

    def timer(self):
        pass

    def update(self, flow=False):
        config = json.dumps(self.parent.clean_config(self.parent.config, flow=flow), indent=4)
        config_original = json.dumps(self.parent.clean_config(self.parent.config_original, flow=flow), indent=4)
        self.jsondiff.clear()
        differ = difflib.Differ()
        color_format = self.jsondiff.currentCharFormat()
        default_color = color_format.foreground()
        last_lines = []
        show_next = 0
        self.found_diffs = False
        for line_n, line in enumerate(differ.compare(config_original.split("\n"), config.split("\n"))):
            marker = line[0]
            show = True
            if marker == "-":
                color = QColor(155, 0, 0)
                cursor = self.jsondiff.textCursor()
                cursor.movePosition(QTextCursor.End)
                self.jsondiff.setTextCursor(cursor)
                self.found_diffs = True
            elif marker == "+":
                color = QColor(0, 155, 0)
                cursor = self.jsondiff.textCursor()
                cursor.movePosition(QTextCursor.End)
                self.jsondiff.setTextCursor(cursor)
                self.found_diffs = True
            elif marker == "?":
                continue
            else:
                color = default_color
                if self.diff_only:
                    show = False
            if show:
                if last_lines:
                    for lline in last_lines[-3:]:
                        self.jsondiff.insertPlainText(lline)
                    last_lines = []
                    show_next = 3
                color_format.setForeground(color)
                self.jsondiff.setCurrentCharFormat(color_format)
                if self.line_numbers:
                    self.jsondiff.insertPlainText(f"{line_n} ")
                self.jsondiff.insertPlainText(f"{line}\n")
            else:
                color_format.setForeground(color)
                self.jsondiff.setCurrentCharFormat(color_format)
                if show_next:
                    if self.line_numbers:
                        self.jsondiff.insertPlainText(f"{line_n} ")
                    self.jsondiff.insertPlainText(f"{line}\n")
                    show_next -= 1
                    if show_next == 0:
                        self.jsondiff.insertPlainText("-----------\n")
                if self.line_numbers:
                    last_lines.append(f"{line_n} {line}\n")
                else:
                    last_lines.append(f"{line}\n")
        if self.diff_only and not self.found_diffs:
            self.jsondiff.insertPlainText("--- NO CHANGES ---\n")


class TabOptions:
    def __init__(self, parent):
        self.parent = parent
        self.config = parent.config
        self.update_flag = False
        self.ini_items = {}
        self.filter_text = ""
        self.items = {}
        self.help_img1 = None
        self.help_img2 = None

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
        self.tab_widget.addTab(self.tab_linuxcnc, "General")
        self.tab_widget.addTab(self.tab_ini, "INI-Defaults")
        self.tab_widget.addTab(self.tab_hal, "HAL-Signals")

        self.treeview = QTreeView()
        self.model = QStandardItemModel()
        self.model.setHorizontalHeaderLabels(["Name", "Value"])
        self.treeview.setModel(self.model)

        hbox_search = QHBoxLayout()
        self.filter_entry = QLineEdit("")
        self.filter_entry.textChanged.connect(self.filter)
        hbox_search.addWidget(QLabel("Filter"))
        hbox_search.addWidget(self.filter_entry)
        self.layout_ini.addLayout(hbox_search)
        self.layout_ini.addWidget(self.treeview)

        self.phal_table = QTableWidget()
        self.phal_table.setColumnCount(5)
        self.phal_table.setHorizontalHeaderItem(0, QTableWidgetItem("Plugin"))
        self.phal_table.setHorizontalHeaderItem(1, QTableWidgetItem("Signal"))
        self.phal_table.setHorizontalHeaderItem(2, QTableWidgetItem("Halpin/Value"))
        self.phal_table.setHorizontalHeaderItem(3, QTableWidgetItem("Type"))
        self.phal_table.setHorizontalHeaderItem(4, QTableWidgetItem("Action"))
        self.layout_hal.addWidget(self.phal_table)
        self.phal_table.itemChanged.connect(self.table_updated)

        self.hal_table = QTableWidget()
        self.hal_table.setColumnCount(3)
        self.hal_table.setHorizontalHeaderItem(0, QTableWidgetItem("Target"))
        self.hal_table.setHorizontalHeaderItem(1, QTableWidgetItem("Source"))
        self.hal_table.setHorizontalHeaderItem(2, QTableWidgetItem("Type"))
        self.layout_hal.addWidget(self.hal_table)
        self.hal_table.itemChanged.connect(self.table_updated)

    def filter(self, text):
        self.filter_text = text
        self.update(full=True)

    def update(self, config=None, full=False):
        if self.update_flag:
            return
        self.update_flag = True
        if config is not None:
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
        self.load_tree_linuxcnc_ini(self.model, full)
        self.treeview.resizeColumnToContents(0)
        self.treeview.header().setStretchLastSection(True)

        # hal
        row = 0
        self.hal_table.setRowCount(1 + len(self.config["linuxcnc"].get("net", [])) + len(self.config["linuxcnc"].get("setp", {}).keys()))
        for entry in self.config["linuxcnc"].get("net", []):
            source = entry.get("source", "")
            target = entry.get("target", "")
            self.hal_table.setItem(row, 0, QTableWidgetItem(target))
            self.hal_table.setItem(row, 1, QTableWidgetItem(source))
            if source.replace(".", "").lstrip("-").lstrip("-").isnumeric():
                item = QTableWidgetItem("setp")
            else:
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

        self.comboBoxes = {}

        def signal_clear(sconf):
            if "net" in sconf:
                del sconf["net"]
            if "setp" in sconf:
                del sconf["setp"]
            self.updated()

        row = 0
        for sitem in self.parent.scene.items():
            if hasattr(sitem, "plugin_instance"):
                plugin_config = sitem.plugin_instance.plugin_setup
                uid = sitem.plugin_instance.plugin_setup["uid"]
                # if plugin_config.get("is_joint") is True:
                #    continue
                for signal in sitem.plugin_instance.SIGNALS:
                    sconf = plugin_config.get("signals", {}).get(signal, {})
                    self.phal_table.setRowCount(row + 1)
                    net = sconf.get("net")
                    setp = sconf.get("setp")
                    item = QTableWidgetItem(uid)
                    item.setFlags(Qt.ItemFlag.ItemIsEnabled)
                    self.phal_table.setItem(row, 0, item)
                    item = QTableWidgetItem(signal)
                    item.setFlags(Qt.ItemFlag.ItemIsEnabled)
                    self.phal_table.setItem(row, 1, item)

                    value = ""
                    itype = ""
                    if net:
                        value = net
                        itype = "net"
                    elif setp:
                        value = setp
                        itype = "setp"

                    self.phal_table.setItem(row, 2, QTableWidgetItem())
                    self.comboBoxes[row] = SearchComboBox(self.table_updated)
                    self.comboBoxes[row].addItem(str(value))

                    for signal_direction in ("input", "output"):
                        for halpin, halpin_info in riocore.halpins.LINUXCNC_SIGNALS[signal_direction].items():
                            self.comboBoxes[row].addItem(halpin)

                    self.phal_table.setCellWidget(row, 2, self.comboBoxes[row])
                    self.comboBoxes[row].currentIndexChanged.connect(self.table_updated)
                    self.comboBoxes[row].textActivated.connect(self.table_updated)

                    item = QTableWidgetItem(itype)
                    item.setFlags(Qt.ItemFlag.ItemIsEnabled)
                    self.phal_table.setItem(row, 3, item)

                    self.phal_table.setItem(row, 4, QTableWidgetItem())
                    if sconf and value:
                        button = QPushButton("clear")
                        button.setFixedWidth(60)
                        button.clicked.connect(partial(partial(signal_clear, sconf)))
                        self.phal_table.setCellWidget(row, 4, button)

                    row += 1

        self.phal_table.resizeColumnToContents(0)
        self.phal_table.resizeColumnToContents(1)
        self.phal_table.resizeColumnToContents(3)
        self.phal_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.phal_table.resizeColumnToContents(4)

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
        if os.path.exists(os.path.join(riocore_path, path)) or os.path.exists(os.path.join(riocore_path, "riocore", path)):
            return os.path.join(riocore_path, path)
        riocore.log(f"can not find path: {path}")
        # exit(1)

    def remove_ini_entry(self, section, key):
        confirmation = QMessageBox.question(self.parent, "Confirmation", f"realy remove {key} from {section} ?", QMessageBox.Yes | QMessageBox.No)
        if confirmation == QMessageBox.Yes and key in self.config["linuxcnc"]["ini"][section]:
            del self.config["linuxcnc"]["ini"][section][key]
            self.parent.cfg_check()
            self.update(self.config, True)

    def add_ini_entry(self, section):
        dialog = QDialog()
        dialog.setWindowTitle("add entry")
        dialog.setMinimumWidth(500)
        dialog.layout = QVBoxLayout()
        dialog.setLayout(dialog.layout)
        dialog_buttonBox = QDialogButtonBox(QDialogButtonBox.Cancel | QDialogButtonBox.Ok)
        dialog_buttonBox.accepted.connect(dialog.accept)
        dialog_buttonBox.rejected.connect(dialog.reject)

        vbox = QVBoxLayout()

        hbox = QHBoxLayout()
        hbox.addWidget(QLabel("Section"), stretch=1)
        section_w = QLineEdit(section.upper())
        hbox.addWidget(section_w, stretch=2)
        vbox.addLayout(hbox)

        hbox = QHBoxLayout()
        hbox.addWidget(QLabel("Name"), stretch=1)
        name_w = QLineEdit("")
        hbox.addWidget(name_w, stretch=2)
        vbox.addLayout(hbox)

        hbox = QHBoxLayout()
        hbox.addWidget(QLabel("Value"), stretch=1)
        value_w = QLineEdit("")
        hbox.addWidget(value_w, stretch=2)
        vbox.addLayout(hbox)

        dialog.layout.addLayout(vbox)
        dialog.layout.addWidget(dialog_buttonBox)

        if dialog.exec():
            section = section_w.text().upper()
            name = name_w.text()
            value = value_w.text()
            if section and name and value:
                if section not in self.config["linuxcnc"]["ini"]:
                    self.config["linuxcnc"]["ini"][section] = {}
                self.config["linuxcnc"]["ini"][section][name] = value
                self.parent.cfg_check()
                self.update(self.config, True)

    def load_tree_linuxcnc_ini(self, parent_tree, full=False):
        if "ini" not in self.config["linuxcnc"]:
            self.config["linuxcnc"]["ini"] = {}
        ini_config = self.config["linuxcnc"]["ini"]

        ini_data = riocore.generator.LinuxCNC.LinuxCNC.ini_defaults(self.config)

        if self.ini_items and not full:
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

        self.ini_items = {}
        tree_lcncini = parent_tree
        tree_lcncini.removeRows(0, tree_lcncini.rowCount())

        for section, section_data in ini_data.items():
            if section not in ini_config:
                ini_config[section] = {}
            section_config = ini_config[section]

            aitem = MyStandardItem()
            tree_lcncini.appendRow(
                [
                    aitem,
                    MyStandardItem(""),
                ]
            )

            widget = QWidget()
            hbox = QHBoxLayout()
            label = QLabel(section)
            hbox.addWidget(label, stretch=1)
            button = QPushButton("add entry")
            button.setFixedWidth(120)
            button.clicked.connect(partial(partial(self.add_ini_entry, section)))
            hbox.addWidget(button, stretch=0)
            widget.setLayout(hbox)
            self.treeview.setIndexWidget(aitem.index(), widget)

            lcncsec_view = tree_lcncini.item(tree_lcncini.rowCount() - 1)
            for key, value in section_data.items():
                if self.filter_text and self.filter_text.lower() not in key.lower():
                    continue

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
                    bitem = MyStandardItem()
                    lcncsec_view.appendRow(
                        [
                            aitem,
                            bitem,
                        ]
                    )
                    widget = QWidget()
                    hbox = QHBoxLayout()
                    label = QLabel(key_title)
                    hbox.addWidget(label, stretch=1)
                    if key in self.config["linuxcnc"]["ini"][section]:
                        button = QPushButton("remove")
                        button.setFixedWidth(120)
                        button.clicked.connect(partial(partial(self.remove_ini_entry, section, key)))
                        hbox.addWidget(button, stretch=0)
                    widget.setLayout(hbox)
                    self.treeview.setIndexWidget(aitem.index(), widget)

                    widget = self.parent.edit_item(section_config, key, var_setup, cb=self.updated)
                    self.treeview.setIndexWidget(bitem.index(), widget)

                    self.ini_items[f"{section}_{key}"] = widget
        self.treeview.expandAll()

    def load(self):
        self.interfaces = []

        if "linuxcnc" not in self.config:
            self.config["linuxcnc"] = {}

        hbox = QHBoxLayout()
        self.layout_linuxcnc.addLayout(hbox)

        vbox = QVBoxLayout()
        hbox.addLayout(vbox, stretch=3)

        row = QHBoxLayout()
        vbox.addLayout(row)
        row.addWidget(QLabel("Name"))
        item = self.parent.edit_item(self.config, "name", {"type": str, "default": "Empty", "help_text": "config name"}, cb=self.updated)
        row.addWidget(item)

        for key, var_setup in {
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
            "scurve": {"type": bool, "help_text": "enable scurve support (linuxcnc >= v2.10)", "default": False},
            "debug_info": {"type": bool, "help_text": "Displays some debug infos in VCP", "default": False},
        }.items():
            row = QHBoxLayout()
            vbox.addLayout(row)
            label = QLabel(key.replace("_", " ").title())
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
        for row in range(nrows):
            target = str(self.hal_table.item(row, 0).text())
            source = str(self.hal_table.item(row, 1).text())
            if target:
                self.config["linuxcnc"]["net"].append(
                    {
                        "source": source,
                        "target": target,
                    }
                )
                if target in self.config["linuxcnc"]["setp"]:
                    del self.config["linuxcnc"]["setp"][target]

        # plugin signals
        nrows = self.phal_table.rowCount()
        signals = {}
        for row in range(nrows):
            if self.phal_table.item(row, 1) and self.phal_table.item(row, 2):
                uid = str(self.phal_table.item(row, 0).text())
                source = str(self.phal_table.item(row, 1).text())
                target = str(self.comboBoxes[row].currentText())
                if target:
                    if uid not in signals:
                        signals[uid] = {}
                    signals[uid][source] = target
        for item in self.parent.scene.items():
            if hasattr(item, "plugin_instance"):
                plugin_setup = item.plugin_instance.plugin_setup
                uid = item.plugin_instance.plugin_setup["uid"]
                if uid in signals:
                    for target, source in signals[uid].items():
                        if "signals" not in plugin_setup:
                            plugin_setup["signals"] = {}
                        if target not in plugin_setup["signals"]:
                            plugin_setup["signals"][target] = {}
                        if "setp" in plugin_setup["signals"][target]:
                            # moved into net / splitted later in hal-generator
                            plugin_setup["signals"][target]["setp"]
                        plugin_setup["signals"][target]["net"] = source

        self.updated()

    def updated(self, tmp=None):
        self.parent.redraw()
        self.parent.cfg_check()
        self.update(self.config)

    def widget(self):
        return self.tab_widget
