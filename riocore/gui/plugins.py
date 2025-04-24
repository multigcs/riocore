import copy
import importlib
import os
from functools import partial

import riocore
from riocore import halpins

from riocore.widgets import (
    MyStandardItem,
    STYLESHEET,
    STYLESHEET_TABBAR,
)

from PyQt5 import QtSvg
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QPixmap
from PyQt5.QtWidgets import (
    QHeaderView,
    QGroupBox,
    QLineEdit,
    QDialog,
    QDialogButtonBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QTableWidget,
    QTableWidgetItem,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

riocore_path = os.path.dirname(riocore.__file__)


class GuiPlugins:
    def __init__(self, parent):
        self.parent = parent

    def edit_plugin_pins(self, plugin_instance, plugin_config):
        def update(arg):
            pass
            # print("#update", arg, plugin_config)

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

            frame = QGroupBox()
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

            pin_cols.addWidget(self.parent.edit_item(pin_config, "pin", {"type": "select", "options": self.parent.pinlist, "default": ""}, cb=update), stretch=6)
            if direction == "input":
                pin_cols.addWidget(QLabel("Pull:"), stretch=1)
                pin_cols.addWidget(self.parent.edit_item(pin_config, "pull", {"type": "select", "options": [None, "up", "down"], "default": None}, cb=update), stretch=3)
            else:
                pin_cols.addWidget(QLabel(""), stretch=4)

            # Modifiers
            if "modifier" not in pin_config:
                pin_config["modifier"] = []
            modifier_list = pin_config["modifier"]

            pin_cols = QHBoxLayout()
            pin_rows.addLayout(pin_cols)
            mod_label = QLabel("Modifiers:")
            mod_label.setToolTip("list of pin-modifiers")
            pin_cols.addWidget(mod_label)
            mod_cols = QHBoxLayout()
            pin_cols.addLayout(mod_cols)
            add_button = QPushButton("+")
            add_button.setToolTip("add an pin-modifiers")
            add_button.clicked.connect(partial(self.parent.gui_modifiers.modifier_list_add, mod_cols, modifier_list))
            add_button.setFixedWidth(20)
            pin_cols.addWidget(add_button)
            pin_cols.addStretch()
            self.parent.gui_modifiers.modifier_list_update(mod_cols, modifier_list)

            # IO-Standart
            pin_cols = QHBoxLayout()
            pin_rows.addLayout(pin_cols)
            tooltip = "FPGA level IO config / optional / better do not use :)"
            io_label = QLabel("IO-Standart:")
            io_label.setToolTip(tooltip)
            pin_cols.addWidget(io_label, stretch=1)

            pin_cols.addWidget(
                self.parent.edit_item(
                    pin_config, "iostandard", {"type": "select", "options": ["LVTTL", "LVCMOS33", "LVCMOS25", "LVCMOS18", "LVCMOS15", "LVCMOS12"], "default": "LVTTL", "help_text": tooltip}, cb=update
                ),
                stretch=3,
            )
            if direction == "output":
                label = QLabel("Slew:")
                label.setToolTip(tooltip)
                pin_cols.addWidget(label, stretch=1)
                pin_cols.addWidget(self.parent.edit_item(pin_config, "slew", {"type": "select", "options": ["SLOW", "FAST"], "default": "SLOW", "help_text": tooltip}, cb=update), stretch=3)
                label = QLabel("Drive:")
                label.setToolTip(tooltip)
                pin_cols.addWidget(label, stretch=1)
                pin_cols.addWidget(
                    self.parent.edit_item(pin_config, "drive", {"type": "select", "options": ["2", "4", "8", "12", "16", "24"], "default": "4", "help_text": tooltip}, cb=update), stretch=3
                )
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

    def edit_plugin_joints(self, plugin_instance, plugin_config):
        def update(arg):
            svgWidget.load(self.parent.draw_joint_home(joints_setup, joint_options))

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

        for key, value in riocore.generator.LinuxCNC.LinuxCNC.PID_DEFAULTS.items():
            pkey = f"pid_{key.lower()}"
            joint_options[pkey] = {}
            joint_options[pkey]["type"] = float
            joint_options[pkey]["default"] = value

        joint_tabs = QTabWidget()
        joint_tabs.setStyleSheet(STYLESHEET_TABBAR)

        general_layout = QVBoxLayout()
        label = QLabel("Joint-Setup")
        label.setFont(myFont)
        general_layout.addWidget(label)

        for option, option_setup in joint_options.items():
            if option.startswith("home"):
                continue
            if option.startswith("pid_"):
                continue
            tootltip = halpins.INI_HELPTEXT["JOINT_NUM"].get(option.upper(), f"{option} config")
            option_row = QHBoxLayout()
            option_label = QLabel(option.replace("_", "-").title())
            option_label.setToolTip(tootltip)
            option_row.addWidget(option_label, stretch=1)

            if option == "feedback":
                options = [""]
                for plugin_instance in self.parent.plugins.plugin_instances:
                    for signal_name, signal_config in plugin_instance.signals().items():
                        if signal_name == "position":
                            options.append(f"{plugin_instance.title}:{signal_name}")
                option_setup = {"type": "select", "options": options, "default": ""}
                option_widget = self.parent.edit_item(joints_setup, option, option_setup, cb=update, help_text=tootltip)
            else:
                option_widget = self.parent.edit_item(joints_setup, option, option_setup, cb=update, help_text=tootltip)

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
            if option == "home_sequence":
                option_setup = {"default": "auto", "type": "select", "options": ["auto"] + [str(n) for n in range(-9, 9)]}
            option_widget = self.parent.edit_item(joints_setup, option, option_setup, cb=update, help_text=tootltip)
            option_row.addWidget(option_widget, stretch=3)
            homing_layout.addLayout(option_row)

        svgWidget = QtSvg.QSvgWidget()
        update(None)
        homing_layout.addStretch()
        homing_layout.addWidget(svgWidget)

        homing_tab = QWidget()
        homing_tab.setLayout(homing_layout)
        joint_tabs.addTab(homing_tab, "Homing")

        pid_layout = QVBoxLayout()
        label = QLabel("Joint-PID")
        label.setFont(myFont)
        pid_layout.addWidget(label)
        for option, option_setup in joint_options.items():
            if not option.startswith("pid_"):
                continue
            tootltip = halpins.INI_HELPTEXT["JOINT_NUM"].get(option.upper(), f"{option} config")
            option_row = QHBoxLayout()
            option_label = QLabel(option.replace("_", "-").title())
            option_label.setToolTip(tootltip)
            option_row.addWidget(option_label, stretch=1)
            option_widget = self.parent.edit_item(joints_setup, option, option_setup, cb=update, help_text=tootltip)
            option_row.addWidget(option_widget, stretch=3)
            pid_layout.addLayout(option_row)
        pid_layout.addStretch()

        pid_tab = QWidget()
        pid_tab.setLayout(pid_layout)
        joint_tabs.addTab(pid_tab, "PID")

        return joint_tabs

    def edit_plugin_signals(self, plugin_instance, plugin_config):
        def update(arg):
            pass
            # print("#update", arg, plugin_config)

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

            frame = QGroupBox()
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
            signal_cols.addWidget(self.parent.edit_item(signals_setup[signal_name], "net", signal_setup["net"], cb=update), stretch=5)

            signal_cols = QHBoxLayout()
            signal_rows.addLayout(signal_cols)
            signal_cols.addWidget(QLabel("Function:"), stretch=1)
            signal_setup["function"] = {"type": "select", "options": options_func}
            signal_cols.addWidget(self.parent.edit_item(signals_setup[signal_name], "function", signal_setup["function"], cb=update), stretch=5)

            if signal_direction == "output":
                signal_cols.addWidget(QLabel("setp:"), stretch=1)
                signal_setup["setp"] = {"type": str, "default": ""}
                signal_cols.addWidget(self.parent.edit_item(signals_setup[signal_name], "setp", signal_setup["setp"], cb=update), stretch=1)

            signal_cols = QHBoxLayout()
            signal_rows.addLayout(signal_cols)
            signal_cols.addWidget(QLabel("MQTT:"), stretch=1)
            signal_setup["mqtt"] = {"type": bool, "default": False, "help_text": "add this signal to the mqtt-publisher"}
            signal_cols.addWidget(self.parent.edit_item(signals_setup[signal_name], "mqtt", signal_setup["mqtt"], cb=update), stretch=5)

            signal_cols = QHBoxLayout()
            signal_rows.addLayout(signal_cols)

            if "source" not in signal_defaults and not signal_defaults.get("bool"):
                signal_cols.addWidget(QLabel("Scale"), stretch=1)
                signal_setup["scale"] = {"type": float, "default": 1.0}
                signal_cols.addWidget(self.parent.edit_item(signals_setup[signal_name], "scale", signal_setup["scale"], cb=update), stretch=4)

                signal_cols.addWidget(QLabel("Offset"), stretch=1)
                signal_setup["offset"] = {"type": float, "default": 0.0}
                signal_cols.addWidget(self.parent.edit_item(signals_setup[signal_name], "offset", signal_setup["offset"], cb=update), stretch=5)

            if not signal_defaults.get("bool") and signal_direction == "input":
                signal_cols = QHBoxLayout()
                signal_rows.addLayout(signal_cols)
                signal_cols.addWidget(QLabel("AVG-Filter"), stretch=1)
                signal_setup["filters"] = {"type": "avgfilter", "default": 0}
                signal_cols.addWidget(self.parent.edit_item(signals_setup[signal_name], "filters", signal_setup["filters"], cb=update), stretch=5)

            display_frame = QGroupBox()
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

            expand = False
            if signals_setup[signal_name]["display"]:
                expand = True

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
                display_setup["initval"] = {"type": float, "default": 0.0}
            for option, option_setup in display_setup.items():
                display_cols = QHBoxLayout()
                display_rows.addLayout(display_cols)
                display_cols.addWidget(QLabel(option.title()), stretch=1)
                display_cols.addWidget(self.parent.edit_item(signals_setup[signal_name]["display"], option, option_setup, cb=None), stretch=5)

            if expand is True:
                display_frame.setChecked(True)
                toggleGroup(display_frame)

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
            option_row.addWidget(self.parent.edit_item(plugin_config, option_name, option_defaults, cb=update), stretch=3)

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
        dialog.setWindowTitle(f"edit plugin {plugin_instance.NAME}")
        dialog.setStyleSheet(STYLESHEET)
        dialog_buttonBox = QDialogButtonBox(QDialogButtonBox.Cancel | QDialogButtonBox.Ok)
        dialog_buttonBox.accepted.connect(dialog.accept)
        dialog_buttonBox.rejected.connect(dialog.reject)

        if not nopins:
            remove_button = QPushButton(self.parent.tr("Remove"))
            remove_button.clicked.connect(partial(self.del_plugin, plugin_instance, dialog=dialog))
            dialog_buttonBox.addButton(remove_button, QDialogButtonBox.ActionRole)

        tab_widget = QTabWidget()
        tab_widget.setStyleSheet(STYLESHEET_TABBAR)

        if is_new and plugin_instance.TYPE == "joint":
            if "position" in plugin_instance.SIGNALS:
                plugin_config["is_joint"] = True

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
        if plugin_instance.TYPE != "interface":
            if plugin_instance.SIGNALS:
                signals_tab = self.edit_plugin_signals(plugin_instance, plugin_config)
                tab_widget.addTab(signals_tab, "Signals")

        right_layout = QVBoxLayout()
        plugin_path = os.path.join(riocore_path, "plugins", plugin_instance.NAME)
        image_path = os.path.join(plugin_path, "image.png")
        if os.path.isfile(image_path):
            ilabel = QLabel()
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
            self.parent.config_load()
            # self.parent.display()
            return
        if not dialog.is_removed:
            for key in list(plugin_config.keys()):
                if key not in plugin_config_backup:
                    del plugin_config[key]
            for key in plugin_config_backup:
                plugin_config[key] = plugin_config_backup[key]

    def config_plugin(self, plugin_instance, plugin_id, widget):
        if os.path.isfile(os.path.join(riocore_path, "plugins", plugin_instance.NAME, "config.py")):
            plugin_config = importlib.import_module(".config", f"riocore.plugins.{plugin_instance.NAME}")
            config_box = plugin_config.config(plugin_instance, styleSheet=STYLESHEET)
            config_box.run()
        self.parent.config_load()
        # self.parent.load_tree()
        # self.parent.display()

    def add_plugin(self, pin_id, slot_name=None):
        boardcfg = self.parent.config.get("boardcfg")
        toolchain = self.parent.board.get("toolchain")
        family = self.parent.board.get("family")
        plugin_needs = {}
        plugin_list = self.parent.plugins.list()
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
                "keywords": plugins.plugin_instances[0].KEYWORDS,
                "pins": plugins.plugin_instances[0].PINDEFAULTS,
                "signals": plugins.plugin_instances[0].SIGNALS,
            }

        possible_plugins = []
        if slot_name:
            # filter possible plugins if slot is set
            for slot in self.parent.slots:
                if slot_name == slot["name"]:
                    compatible = slot.get("compatible")
                    if compatible:
                        possible_plugins = compatible
                    else:
                        # default = slot.get("default")
                        # if default:
                        #    possible_plugins.append(default)
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
        dialog_buttonBox = QDialogButtonBox(QDialogButtonBox.Cancel | QDialogButtonBox.Ok)
        dialog_buttonBox.accepted.connect(dialog.accept)
        dialog_buttonBox.rejected.connect(dialog.reject)

        if slot_name:

            def add_module():
                dialog.close()
                self.parent.add_module(None, slot_name=slot_name, slot_select=False)

            slot_button = QPushButton(self.parent.tr("use module selection"))
            slot_button.clicked.connect(add_module)
            dialog_buttonBox.addButton(slot_button, QDialogButtonBox.ActionRole)

        dialog.setLayout(dialog.layout)

        def show_plugin_info(idx):
            if not plugin_table.item(idx, 1):
                return

            plugin_name = plugin_table.item(idx, 1).text()
            plugin_path = os.path.join(riocore_path, "plugins", plugin_name)
            image_path = os.path.join(plugin_path, "image.png")
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

            try:
                description = md2label(description)
            except Exception as error:
                print(f"ERROR: formating description: {error}")
                print(description)

            description_label.setText(description)
            dialog.selected = plugin_name

        def search(search_str):
            plugin_table.setRowCount(0)
            row = 0
            for plugin_name in possible_plugins:
                stext = f"{plugin_name} {plugin_infos[plugin_name]['info']} {plugin_infos[plugin_name]['description']} {plugin_infos[plugin_name]['keywords']}"
                if search_str.lower() not in stext.lower():
                    continue
                plugin_table.setRowCount(row + 1)
                plugin_table.setItem(row, 0, QTableWidgetItem(""))
                plugin_table.setItem(row, 1, QTableWidgetItem(plugin_name))
                plugin_path = os.path.join(riocore_path, "plugins", plugin_name)
                image_path = os.path.join(plugin_path, "image.png")
                if os.path.isfile(image_path):
                    ilabel = QLabel()
                    ilabel.setFixedSize(24, 24)
                    pixmap = QPixmap(image_path)
                    ilabel.setPixmap(pixmap)
                    ilabel.setScaledContents(True)
                    plugin_table.setCellWidget(row, 0, ilabel)
                row += 1
            if row > 0:
                show_plugin_info(0)

        plugin_table = QTableWidget()
        plugin_table.setColumnCount(2)
        plugin_table.verticalHeader().setVisible(False)
        plugin_table.setHorizontalHeaderItem(0, QTableWidgetItem(""))
        plugin_table.setHorizontalHeaderItem(1, QTableWidgetItem("Name"))
        plugin_table.setRowCount(len(possible_plugins))
        for row, plugin_name in enumerate(possible_plugins):
            plugin_table.setItem(row, 0, QTableWidgetItem(""))
            plugin_table.setItem(row, 1, QTableWidgetItem(plugin_name))
            plugin_path = os.path.join(riocore_path, "plugins", plugin_name)
            image_path = os.path.join(plugin_path, "image.png")
            if os.path.isfile(image_path):
                ilabel = QLabel()
                ilabel.setFixedSize(24, 24)
                pixmap = QPixmap(image_path)
                ilabel.setPixmap(pixmap)
                ilabel.setScaledContents(True)
                plugin_table.setCellWidget(row, 0, ilabel)

        plugin_table.setFixedWidth(200)
        plugin_table.cellClicked.connect(show_plugin_info)
        plugin_table.currentCellChanged.connect(show_plugin_info)
        header = plugin_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.Stretch)

        mid_layout = QVBoxLayout()
        mid_widget = QWidget()
        mid_widget.setMinimumWidth(400)
        mid_widget.setLayout(mid_layout)
        name_label = QLabel("name")
        name_label_font = QFont()
        name_label_font.setBold(True)
        name_label.setFont(name_label_font)

        mid_layout.addWidget(name_label)
        info_label = QLabel("info")
        mid_layout.addWidget(info_label)
        description_label = QLabel("description")
        description_label.setAlignment(Qt.AlignTop)
        description_scroll = QScrollArea()
        description_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        description_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        description_scroll.setWidgetResizable(True)
        description_scroll.setWidget(description_label)
        mid_layout.addWidget(description_scroll, stretch=1)

        right_layout = QVBoxLayout()
        right_widget = QWidget()
        right_widget.setLayout(right_layout)
        image_label = QLabel()
        right_layout.addWidget(image_label)
        right_layout.addStretch()

        left_layout = QVBoxLayout()
        left_widget = QWidget()
        left_widget.setLayout(left_layout)
        plugin_search = QLineEdit("")
        plugin_search.textChanged.connect(search)
        left_layout.addWidget(plugin_search)
        left_layout.addWidget(plugin_table, stretch=1)

        infos = QHBoxLayout()
        infos.addWidget(left_widget, stretch=0)
        infos.addWidget(mid_widget, stretch=3)
        infos.addWidget(right_widget, stretch=0)

        dialog.layout.addLayout(infos)
        dialog.layout.addWidget(dialog_buttonBox)

        show_plugin_info(0)

        if dialog.exec():
            plugin_id = len(self.parent.config["plugins"])
            self.parent.config["plugins"].append(
                {
                    "type": dialog.selected,
                    "pins": {},
                }
            )
            plugin_config = self.parent.config["plugins"][plugin_id]

            uid_prefix = plugin_config["type"]
            unum = 0
            while f"{uid_prefix}{unum}" in self.parent.plugin_uids:
                unum += 1
            self.parent.plugin_uids.append(f"{uid_prefix}{unum}")
            plugin_config["uid"] = f"{uid_prefix}{unum}"

            plugin_instance = self.parent.plugins.load_plugin(plugin_id, plugin_config, self.parent.config)

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
                        if self.parent.get_plugin_by_pin(spin["pin"]) == (None, None):
                            if direction:
                                slotpins[direction].append(spin_name)

                    # map single pin plugin to pin_id
                    num_mandatory = 0
                    for pin_name, pin_defaults in plugin_instance.PINDEFAULTS.items():
                        optional = pin_defaults.get("optional")
                        if optional is True:
                            continue
                        num_mandatory += 1

                    # workaround for too many pins on slot
                    if len(slot.get("pins", {}).keys()) > 10:
                        num_mandatory = 1

                    if num_mandatory == 1:
                        for pin_name, pin_defaults in plugin_instance.PINDEFAULTS.items():
                            optional = pin_defaults.get("optional")
                            if optional is True:
                                continue
                            direction = pin_defaults.get("direction") or "all"
                            pinconfig = {"pin": f"{slot_name}:{pin_id}"}
                            if direction in slotpins and pin_id in slotpins[direction]:
                                slotpins[direction].remove(pin_id)
                            self.parent.config["plugins"][plugin_id]["pins"][pin_name] = pinconfig
                            break
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
                            self.parent.config["plugins"][plugin_id]["pins"][pin_name] = pinconfig

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
                            self.parent.config["plugins"][plugin_id]["pins"][pin_name] = pinconfig

                self.tree_add_plugin(self.parent.tree_plugins, plugin_instance, expand=True)
                self.parent.display()

                self.edit_plugin(plugin_instance, None, is_new=True)

            return dialog.selected

    def del_plugin(self, plugin_instance, widget, dialog=None):
        plugin_id = plugin_instance.plugin_id
        if dialog is not None:
            dialog.is_removed = True
            dialog.close()
        self.parent.config["plugins"].pop(plugin_id)
        self.parent.config_load()
        # self.display()

    def tree_add_plugin(self, parent, plugin_instance, nopins=False, expand=False):
        name = plugin_instance.plugin_setup.get("name")
        if name:
            title = f"{name} ({plugin_instance.NAME})"
        else:
            title = f"{plugin_instance.title} ({plugin_instance.NAME})"
        help_text = plugin_instance.INFO

        plugin_path = os.path.join(riocore_path, "plugins", plugin_instance.NAME)
        image_path = os.path.join(plugin_path, "image.png")

        iconItem = MyStandardItem("", help_text=help_text)
        aitem = MyStandardItem()
        parent.appendRow(
            [
                iconItem,
                aitem,
            ]
        )

        buttons_layout = QHBoxLayout()
        buttons_layout.setContentsMargins(0, 0, 0, 0)
        buttons_widget = QWidget()
        buttons_widget.setLayout(buttons_layout)

        title_layout = QHBoxLayout()
        title_layout.setContentsMargins(0, 0, 0, 0)
        title_widget = QWidget()
        title_widget.setLayout(title_layout)

        ilabel = QLabel()
        ilabel.setFixedSize(24, 24)
        if os.path.isfile(image_path):
            pixmap = QPixmap(image_path)
            ilabel.setPixmap(pixmap)
            ilabel.setScaledContents(True)

        title_layout.addWidget(ilabel)
        title_layout.addWidget(QLabel(title))
        self.parent.treeview.setIndexWidget(iconItem.index(), title_widget)

        # buttons_layout.addWidget(ilabel)

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
        self.parent.treeview.setIndexWidget(aitem.index(), buttons_widget)


def md2label(text):
    hlist = False
    table = False
    formated = []
    table_format = []
    for line in text.split("\n"):
        if not formated and not line.strip():
            continue
        elif not formated:
            formated.append("<html>\n")

        if line.startswith("#"):
            formated.append(f"<h3>{line.strip('#')}<h3><br/>\n")
        elif line.startswith("* "):
            if not hlist:
                formated.append("<ul>\n")
            formated.append(f"<li>{line[2:]}</li>\n")
            hlist = True
        elif line.startswith("|"):
            cols = line.split("|")[1:-1]
            if not table:
                table_format = []
                formated.append("<table border='1'>\n")
            elif not table_format:
                table_format = cols
                continue
            formated.append(" <tr>")
            for col_n, col in enumerate(cols):
                if not table:
                    formated.append(f"<th>{col.strip()}</th>")
                else:
                    col = col.strip()
                    if col and col[0] == "[" and col[-1] == ")" and "](" in col:
                        col = col.split("]")[0][1:]
                    if table_format[col_n].strip() == ":---:":
                        formated.append(f"<td align='center'>{col.strip()}</td>")
                    elif table_format[col_n].strip() == "---:":
                        formated.append(f"<td align='right'>{col.strip()}</td>")
                    else:
                        formated.append(f"<td>{col.strip()}</td>")
            formated.append("</tr>\n")
            table = True
        else:
            if hlist:
                hlist = False
                formated.append("</ul>\n")
            elif table:
                table = False
                formated.append("</table>\n")
            if not line.strip():
                formated.append("<br/>\n")
            else:
                for ch in line:
                    if ch == " ":
                        formated.append("&nbsp;")
                    else:
                        break
                formated.append(f"{line}<br/>\n")
    formated.append("\n</html>\n")
    return "".join(formated)
