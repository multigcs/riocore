import copy
from functools import partial

import riocore
from riocore import halpins
from riocore import components

from riocore.widgets import (
    MyStandardItem,
    STYLESHEET,
    STYLESHEET_TABBAR,
)

from PyQt5 import QtSvg
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (
    QGroupBox,
    QComboBox,
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


class GuiComponents:
    def __init__(self, parent):
        self.parent = parent

    def edit_component_pins(self, cinstance, component):
        def update(arg):
            pass
            # print("#update", arg, plugin_config)

        myFont = QFont()
        myFont.setBold(True)

        pins = QVBoxLayout()
        label = QLabel("Pin-Setup")
        label.setFont(myFont)
        pins.addWidget(label)

        if "pins" not in component:
            component["pins"] = {}

        for pin_name, pin_defaults in cinstance.PINDEFAULTS.items():
            component.get("pins", {}).get(pin_name, {})
            pin_title = pin_name
            direction = pin_defaults["direction"]
            description = pin_defaults.get("description")
            pin_defaults.get("optional", False)
            help_text = f"location for {direction} pin: {pin_name}"

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

            pin_cols.addWidget(self.parent.edit_item(component["pins"], pin_name, {"type": "select", "options": self.parent.gpiolist, "default": ""}, cb=update), stretch=6)

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

    def edit_component_joints(self, cinstance, component):
        def update(arg):
            pass
            # svgWidget.load(self.parent.draw_joint_home(joints_setup, joint_options))

        myFont = QFont()
        myFont.setBold(True)

        if "joint" not in component:
            component["joint"] = {}
        joints_setup = component["joint"]

        joint_options = copy.deepcopy(halpins.JOINT_OPTIONS)
        joint_options.update(copy.deepcopy(halpins.JOINT_OPTIONS_SOFT))

        for key, value in riocore.generator.LinuxCNC.LinuxCNC.JOINT_DEFAULTS.items():
            key = key.lower()
            if key == "scale_out":
                key = "scale"
            if key in joint_options:
                joint_options[key.lower()]["default"] = value

        """
        for key, value in riocore.generator.LinuxCNC.LinuxCNC.PID_DEFAULTS.items():
            pkey = f"pid_{key.lower()}"
            joint_options[pkey] = {}
            joint_options[pkey]["type"] = float
            joint_options[pkey]["default"] = value
        """

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

        return joint_tabs

    def edit_component_signals(self, cinstance, component):
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

        if "signals" not in component:
            component["signals"] = {}
        signals_setup = component["signals"]

        for signal_name, signal_defaults in cinstance.SIGNALS.items():
            # signal_table.setRowCount(row_n + 1)
            if signal_name not in signals_setup:
                signals_setup[signal_name] = {}
            help_text = f"{signal_name} config"

            signal_setup = signal_defaults.get("setup", {})
            signal_direction = signal_defaults["direction"]
            signal_defaults.get("multiplexed", False)
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

            signal_cols = QHBoxLayout()
            signal_rows.addLayout(signal_cols)
            signal_cols.addWidget(QLabel("Net:"), stretch=1)
            signal_setup["net"] = {"type": "select", "options": options_net}
            signal_cols.addWidget(self.parent.edit_item(signals_setup[signal_name], "net", signal_setup["net"], cb=update), stretch=5)

            if signal_direction == "output":
                signal_cols.addWidget(QLabel("setp:"), stretch=1)
                signal_setup["setp"] = {"type": str, "default": ""}
                signal_cols.addWidget(self.parent.edit_item(signals_setup[signal_name], "setp", signal_setup["setp"], cb=update), stretch=1)

            signal_cols = QHBoxLayout()
            signal_rows.addLayout(signal_cols)

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

    def edit_component_options(self, cinstance, component):
        def update(arg):
            # print("#####", arg)
            pass

        myFont = QFont()
        myFont.setBold(True)

        options = QVBoxLayout()

        infotext = cinstance.INFO
        label = QLabel(f"{infotext}\n")
        label.setFont(myFont)
        options.addWidget(label)

        iname_row = QHBoxLayout()
        iname_row.addWidget(QLabel("Name"), stretch=1)
        iname_label = QLabel(component.get("name"))
        iname_row.addWidget(iname_label, stretch=3)
        options.addLayout(iname_row)

        for option_name, option_defaults in cinstance.OPTIONS.items():
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
            option_row.addWidget(self.parent.edit_item(component, option_name, option_defaults, cb=update), stretch=3)

        descriptiontext = cinstance.DESCRIPTION
        label = QLabel(f"{descriptiontext}\n")
        # options.addWidget(label)

        options_widget = QWidget()
        options.addStretch()
        options_widget.setLayout(options)

        options_tab = QScrollArea()
        options_tab.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        options_tab.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        options_tab.setWidgetResizable(True)
        options_tab.setWidget(options_widget)
        return options_tab

    def del_component(self, component, widget, dialog=None):
        if dialog is not None:
            dialog.is_removed = True
            dialog.close()
        for cnum, comp in enumerate(self.parent.config["linuxcnc"]["components"]):
            if comp == component:
                self.parent.config["linuxcnc"]["components"].pop(cnum)
        self.parent.config_load()

    def edit_component(self, component, widget=None, pin_select=None, is_new=False):
        comp_type = component.get("type")
        if hasattr(components, f"comp_{comp_type}"):
            cinstance = getattr(components, f"comp_{comp_type}")(component)
        else:
            return

        component_backup = copy.deepcopy(component)

        dialog = QDialog()
        dialog.is_removed = False
        dialog.setWindowTitle(f"edit component {cinstance.TITLE}")
        dialog.setStyleSheet(STYLESHEET)
        dialog_buttonBox = QDialogButtonBox(QDialogButtonBox.Cancel | QDialogButtonBox.Ok)
        dialog_buttonBox.accepted.connect(dialog.accept)
        dialog_buttonBox.rejected.connect(dialog.reject)

        remove_button = QPushButton(self.parent.tr("Remove"))
        remove_button.clicked.connect(partial(self.del_component, component, dialog=dialog))
        dialog_buttonBox.addButton(remove_button, QDialogButtonBox.ActionRole)

        tab_widget = QTabWidget()
        tab_widget.setStyleSheet(STYLESHEET_TABBAR)

        options_tab = self.edit_component_options(cinstance, component)
        tab_widget.addTab(options_tab, "Options")

        pins_tab = self.edit_component_pins(cinstance, component)
        tab_widget.addTab(pins_tab, "Pins")
        if is_new:
            tab_widget.setCurrentWidget(pins_tab)

        if comp_type == "stepgen":
            joint_tab = self.edit_component_joints(cinstance, component)
            tab_widget.addTab(joint_tab, "Joint")

        else:
            if cinstance.SIGNALS:
                signals_tab = self.edit_component_signals(cinstance, component)
                tab_widget.addTab(signals_tab, "Signals")

        right_layout = QVBoxLayout()
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
            for key in list(component.keys()):
                if key not in component_backup:
                    del component[key]
            for key in component_backup:
                component[key] = component_backup[key]

    def add_component_or_net(self, widget=None, pin_select=None):
        dialog = QDialog()
        dialog.setWindowTitle("select component or set net")

        dialog.layout = QVBoxLayout()
        dialog_buttonBox = QDialogButtonBox(QDialogButtonBox.Cancel | QDialogButtonBox.Ok)
        dialog_buttonBox.accepted.connect(dialog.accept)
        dialog_buttonBox.rejected.connect(dialog.reject)
        dialog.setLayout(dialog.layout)

        combo = QComboBox()
        combo.addItem("Component")
        combo.addItem("Net")
        dialog.layout.addWidget(combo)
        dialog.layout.addWidget(dialog_buttonBox)

        if dialog.exec():
            if combo.currentText() == "Component":
                self.add_component(pin_select=pin_select)
            else:
                if "net" not in self.parent.config["linuxcnc"]:
                    self.parent.config["linuxcnc"]["net"] = []
                net_config = self.parent.config["linuxcnc"]["net"]
                for num, net in enumerate(net_config):
                    if not net.get("source") or not net.get("target"):
                        net_config.pop(num)
                if pin_select.endswith("-out"):
                    net_config.append({"source": "", "target": pin_select})
                else:
                    net_config.append({"source": pin_select, "target": ""})
                self.parent.load_tree("/LinuxCNC/Net/")
                self.self.parent.tabwidget.setCurrentWidget(self.parent.tabs["Config"].widget())

    def add_component(self, widget=None, pin_select=None):
        dialog = QDialog()
        dialog.setWindowTitle("select component")
        dialog.setStyleSheet(STYLESHEET)

        dialog.layout = QVBoxLayout()
        dialog_buttonBox = QDialogButtonBox(QDialogButtonBox.Cancel | QDialogButtonBox.Ok)
        dialog_buttonBox.accepted.connect(dialog.accept)
        dialog_buttonBox.rejected.connect(dialog.reject)
        dialog.setLayout(dialog.layout)

        dialog.component_names = []

        def show_component_info(idx):
            component_name = dialog.component_names[idx]
            info = getattr(components, f"comp_{component_name}").INFO
            description = getattr(components, f"comp_{component_name}").DESCRIPTION
            name_label.setText(info)
            description_label.setText(description)
            dialog.selected = component_name

        component_table = QTableWidget()
        component_table.setColumnCount(1)
        component_table.setHorizontalHeaderItem(0, QTableWidgetItem("components"))

        row_n = 0
        for comp in dir(components):
            if comp.startswith("comp_"):
                component_name = comp.replace("comp_", "")
                getattr(components, comp).INFO
                getattr(components, comp).DESCRIPTION
                component_table.setRowCount(row_n + 1)
                pitem = QTableWidgetItem(component_name)
                component_table.setItem(row_n, 0, pitem)
                dialog.component_names.append(component_name)
                row_n += 1

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

        header = component_table.horizontalHeader()
        header.setStretchLastSection(True)
        # component_table.setFixedWidth(200)
        component_table.cellClicked.connect(show_component_info)
        component_table.currentCellChanged.connect(show_component_info)

        left_layout = QVBoxLayout()
        left_widget = QWidget()
        # left_widget.setFixedWidth(400)
        left_widget.setLayout(left_layout)
        left_layout.addWidget(component_table)

        infos = QHBoxLayout()
        infos.addWidget(left_widget, stretch=0)
        infos.addWidget(mid_widget, stretch=3)
        infos.addWidget(right_widget, stretch=1)

        dialog.layout.addLayout(infos)
        dialog.layout.addWidget(dialog_buttonBox)

        show_component_info(0)
        if dialog.exec():
            if "linuxcnc" not in self.parent.config:
                self.parent.config["linuxcnc"] = {}
            if "components" not in self.parent.config["linuxcnc"]:
                self.parent.config["linuxcnc"] = []

            pins = {}
            self.parent.config["linuxcnc"]["components"].append(
                {
                    "type": dialog.selected,
                    "pins": pins,
                }
            )
            self.parent.load_tree()
            self.edit_component(self.parent.config["linuxcnc"]["components"][-1], is_new=True)

    def tree_add_component(self, parent, component, expand=False):
        comp_type = component.get("type")
        iconItem = MyStandardItem(comp_type, help_text="")
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

        button_edit = QPushButton("edit")
        cb = partial(self.edit_component, component)
        button_edit.clicked.connect(cb)
        button_edit.setMaximumSize(button_edit.sizeHint())
        buttons_layout.addWidget(button_edit)

        button_delete = QPushButton("delete")
        cb = partial(self.del_component, component)
        button_delete.clicked.connect(cb)
        button_delete.setMaximumSize(button_delete.sizeHint())
        buttons_layout.addWidget(button_delete)

        buttons_layout.addStretch()
        self.parent.treeview.setIndexWidget(aitem.index(), buttons_widget)
