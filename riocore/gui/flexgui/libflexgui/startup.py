import os
import sys
import importlib
from functools import partial
import traceback

from PyQt5.QtCore import Qt, QPointF
from PyQt5.QtGui import QRadialGradient, QBrush, QPainter
from PyQt5.QtWidgets import (
    QWidget,
    QAction,
    QLineEdit,
    QSlider,
    QMenu,
    QAbstractButton,
    QPushButton,
    QCheckBox,
    QRadioButton,
    QLabel,
    QLCDNumber,
    QListView,
    QAbstractSpinBox,
    QDoubleSpinBox,
    QSpinBox,
    QGridLayout,
    QVBoxLayout,
    QHBoxLayout,
    QProgressBar,
    QButtonGroup,
)

import linuxcnc as emc
import hal
from libflexgui import led, actions, commands, dialogs, utilities, probe

AXES = ["x", "y", "z", "a", "b", "c", "u", "v", "w"]


def set_screen(parent):
    if parent.settings.contains("GUI/window_size"):
        parent.resize(parent.settings.value("GUI/window_size"))
    if parent.settings.contains("GUI/window_position"):
        parent.move(parent.settings.value("GUI/window_position"))
    else:
        parent.move(0, 0)  # if no settings move window to upper left corner


def setup_vars(parent):
    # put any variables in here that might be called during startup
    parent.selected_style = """
		border-style: inset;
		border-width: 2px;
		border-radius: 1px;
		border-color: gray;
		border-style: solid;"""
    parent.deselected_style = "border-color: transparent;"


def setup_led_buttons(parent):  # LED
    # find led buttons and get any custom properties
    for child in parent.findChildren(QPushButton):
        if child.property("led_indicator"):
            led_dict = {}
            led_dict["name"] = child.objectName()
            led_dict["text"] = child.text()
            led_dict["diameter"] = child.property("led_diameter") or parent.led_diameter
            led_dict["right_offset"] = child.property("led_right_offset") or parent.led_right_offset
            led_dict["top_offset"] = child.property("led_top_offset") or parent.led_top_offset
            led_dict["on_color"] = child.property("led_on_color") or parent.led_on_color
            led_dict["off_color"] = child.property("led_off_color") or parent.led_off_color

            new_button = led.IndicatorButton(**led_dict)
            # determine layout or not
            layout = child.parent().layout()
            if layout:
                index = layout.indexOf(child)
                if index != -1:
                    if isinstance(layout, QGridLayout):
                        row, column, rowspan, columnspan = layout.getItemPosition(index)
                        layout.addWidget(new_button, row, column, rowspan, columnspan)
                    elif isinstance(layout, (QVBoxLayout, QHBoxLayout)):
                        layout.removeWidget(child)
                        layout.insertWidget(index, new_button)
            else:
                geometry = child.geometry()
                child_parent = child.parent()
                new_button.setParent(child_parent)
                new_button.setGeometry(geometry)
            child.deleteLater()
            new_button.setObjectName(led_dict["name"])
            setattr(parent, led_dict["name"], new_button)  # give the new button the old name


def find_children(parent):  # get the object names of all widgets
    parent.children = []
    children = parent.findChildren(QWidget)
    for child in children:
        if child.objectName():
            parent.children.append(child.objectName())
    parent.actions = parent.findChildren(QAction)
    for action in parent.actions:
        if action.objectName():
            parent.children.append(action.objectName())
            if "toolBar" in parent.children:
                widget_name = f"flex_{action.objectName()[6:].replace(' ', '_')}"
                # make sure the action is in the tool bar
                if parent.toolBar.widgetForAction(action) is not None:
                    parent.toolBar.widgetForAction(action).setObjectName(widget_name)
                    setattr(parent, widget_name, parent.toolBar.widgetForAction(action))
                    parent.children.append(widget_name)
    menus = parent.findChildren(QMenu)
    for menu in menus:
        if menu.objectName():
            parent.children.append(menu.objectName())


def update_check(parent):
    if "feedrate_lb" in parent.children:
        msg = "The Feed Override Percent Label object name\nfeedrate_lb has been changed to feed_override_lb.\nChange the name in the ui file.\nThe label will be disabled and will not function."
        print(f"Object Name Changed: {msg}")
        parent.feedrate_lb.setEnabled(False)


def setup_enables(parent):
    parent.home_required = []  # different functions add to this
    parent.state_estop_checked = {}
    parent.state_estop_reset_checked = {}
    # disable home all if home sequence is not found
    if "home_all_pb" in parent.children:
        if not utilities.home_all_check(parent):
            parent.home_all_pb.setEnabled(False)

    # STATE_ESTOP
    parent.state_estop = {
        "power_pb": False,
        "run_pb": False,
        "run_from_line_pb": False,
        "step_pb": False,
        "pause_pb": False,
        "resume_pb": False,
        "jog_selected_plus": False,
        "jog_selected_minus": False,
        "home_all_pb": False,
        "unhome_all_pb": False,
        "run_mdi_pb": False,
        "mdi_s_pb": False,
        "spindle_start_pb": False,
        "spindle_fwd_pb": False,
        "spindle_rev_pb": False,
        "spindle_stop_pb": False,
        "spindle_plus_pb": False,
        "spindle_minus_pb": False,
        "flood_pb": False,
        "mist_pb": False,
        "actionPower": False,
        "actionRun": False,
        "actionRun_From_Line": False,
        "actionStep": False,
        "actionPause": False,
        "tool_change_pb": False,
        "actionResume": False,
        "touchoff_selected_pb": False,
        "touchoff_selected_tool_pb": False,
    }

    for i in range(9):
        parent.state_estop[f"home_pb_{i}"] = False
        parent.state_estop[f"unhome_pb_{i}"] = False
    for axis in AXES:
        parent.state_estop[f"touchoff_pb_{axis}"] = False
        parent.state_estop[f"tool_touchoff_{axis}"] = False
        parent.state_estop[f"zero_{axis}_pb"] = False
    for i in range(100):
        parent.state_estop[f"tool_change_pb_{i}"] = False
    for i in range(1, 10):
        parent.state_estop[f"change_cs_{i}"] = False

    # remove any items not found in the gui
    for item in list(parent.state_estop):
        if item not in parent.children:
            del parent.state_estop[item]

    """ LED
	parent.state_estop_names = {'estop_pb': 'E Stop Open',
		'actionE_Stop': 'E Stop Open', 'power_pb': 'Power Off',
		'actionPower': 'Power Off'}
	"""

    parent.state_estop_names = {}
    if "estop_pb" in parent.children:
        open_text = parent.estop_pb.property("open_text")
        if open_text is not None:
            parent.state_estop_names["estop_pb"] = open_text

    if "power_pb" in parent.children:
        off_text = parent.power_pb.property("off_text")
        if off_text is not None:
            parent.state_estop_names["power_pb"] = off_text

    # remove any items not found in the gui
    for item in list(parent.state_estop_names):
        if item not in parent.children:
            del parent.state_estop_names[item]

    # STATE_ESTOP_RESET enable power
    parent.state_estop_reset = {
        "power_pb": True,
        "run_pb": False,
        "run_from_line_pb": False,
        "step_pb": False,
        "pause_pb": False,
        "resume_pb": False,
        "jog_selected_plus": False,
        "jog_selected_minus": False,
        "home_all_pb": False,
        "unhome_all_pb": False,
        "run_mdi_pb": False,
        "mdi_s_pb": False,
        "spindle_start_pb": False,
        "spindle_fwd_pb": False,
        "spindle_rev_pb": False,
        "spindle_stop_pb": False,
        "spindle_plus_pb": False,
        "spindle_minus_pb": False,
        "flood_pb": False,
        "mist_pb": False,
        "actionPower": True,
        "actionRun": False,
        "actionRun_From_Line": False,
        "actionStep": False,
        "actionPause": False,
        "tool_change_pb": False,
        "actionResume": False,
        "touchoff_selected_pb": False,
        "touchoff_selected_tool_pb": False,
    }

    for i in range(9):
        parent.state_estop_reset[f"home_pb_{i}"] = False
        parent.state_estop_reset[f"unhome_pb_{i}"] = False
    for item in AXES:
        parent.state_estop_reset[f"touchoff_pb_{item}"] = False
        parent.state_estop_reset[f"tool_touchoff_{item}"] = False
    for i in range(100):
        parent.state_estop_reset[f"tool_change_pb_{i}"] = False
    for i in range(1, 10):
        parent.state_estop_reset[f"change_cs_{i}"] = False

    # remove any items not found in the gui
    for item in list(parent.state_estop_reset):
        if item not in parent.children:
            del parent.state_estop_reset[item]

    """ LED
	parent.state_estop_reset_names = {
		'estop_pb': 'E Stop Closed', 'actionE_Stop': 'E Stop Closed',
		'power_pb': 'Power Off', 'actionPower': 'Power Off'
		}
	"""

    parent.state_estop_reset_names = {}
    if "estop_pb" in parent.children:
        closed_text = parent.estop_pb.property("closed_text")
        if closed_text is not None:
            parent.state_estop_reset_names["estop_pb"] = closed_text

    if "power_pb" in parent.children:
        off_text = parent.power_pb.property("off_text")
        if off_text is not None:
            parent.state_estop_reset_names["power_pb"] = off_text

    # remove any items not found in the gui
    for item in list(parent.state_estop_reset_names):
        if item not in parent.children:
            del parent.state_estop_reset_names[item]

    # STATE_ON home, jog, spindle
    parent.state_on = {
        "power_pb": True,
        "run_pb": False,
        "run_from_line_pb": False,
        "step_pb": False,
        "pause_pb": False,
        "resume_pb": False,
        "jog_selected_plus": True,
        "jog_selected_minus": True,
        "spindle_start_pb": True,
        "spindle_fwd_pb": True,
        "spindle_rev_pb": True,
        "spindle_stop_pb": True,
        "spindle_plus_pb": True,
        "spindle_minus_pb": True,
        "flood_pb": True,
        "mist_pb": True,
        "actionPower": True,
        "actionRun": False,
        "actionRun_From_Line": False,
        "actionStep": False,
        "actionPause": False,
        "actionResume": False,
        "touchoff_selected_pb": True,
    }

    # remove any items not found in the gui
    for item in list(parent.state_on):
        if item not in parent.children:
            del parent.state_on[item]

    parent.state_on_names = {}
    if "estop_pb" in parent.children:
        closed_text = parent.estop_pb.property("closed_text")
        if closed_text is not None:
            parent.state_on_names["estop_pb"] = closed_text

    if "power_pb" in parent.children:
        on_text = parent.power_pb.property("on_text")
        if on_text is not None:
            parent.state_on_names["power_pb"] = on_text

    # remove any items not found in the gui
    for item in list(parent.state_on_names):
        if item not in parent.children:
            del parent.state_on_names[item]

    # run controls used to enable/disable when not running a program
    run_items = [
        "open_pb",
        "run_pb",
        "run_from_line_pb",
        "step_pb",
        "run_mdi_pb",
        "reload_pb",
        "actionOpen",
        "menuRecent",
        "actionReload",
        "actionRun",
        "actionRun_From_Line",
        "actionStep",
        "tool_change_pb",
    ]
    for i in range(100):
        run_items.append(f"tool_change_pb_{i}")
    for item in AXES:
        run_items.append(f"tool_touchoff_{item}")
        run_items.append(f"touchoff_pb_{item}")
    parent.run_controls = []
    for item in run_items:
        if item in parent.children:
            parent.run_controls.append(item)

    home_items = []
    if utilities.home_all_check(parent):
        home_items.append("home_all_pb")
    for i in range(9):
        home_items.append(f"home_pb_{i}")
    parent.home_controls = []
    for item in home_items:
        if item in parent.children:
            parent.home_controls.append(item)

    unhome_items = ["unhome_all_pb"]
    for i in range(9):
        unhome_items.append(f"unhome_pb_{i}")
    parent.unhome_controls = []
    for item in unhome_items:
        if item in parent.children:
            parent.unhome_controls.append(item)

    parent.program_running = {
        "open_pb": False,
        "reload_pb": False,
        "run_pb": False,
        "run_from_line_pb": False,
        "step_pb": False,
        "pause_pb": True,
        "jog_selected_plus": False,
        "jog_selected_minus": False,
        "resume_pb": False,
        "run_mdi_pb": False,
        "home_all_pb": False,
        "actionRun": False,
        "actionOpen": False,
        "menuRecent": False,
        "actionReload": False,
        "actionRun_From_Line": False,
        "actionStep": False,
        "actionPause": True,
        "actionResume": False,
        "flood_pb": False,
        "mist_pb": False,
        "unhome_all_pb": False,
        "spindle_start_pb": False,
        "spindle_fwd_pb": False,
        "spindle_rev_pb": False,
        "spindle_stop_pb": False,
        "spindle_plus_pb": False,
        "spindle_minus_pb": False,
        "tool_change_pb": False,
    }

    for i in range(9):
        parent.program_running[f"home_pb_{i}"] = False
        parent.program_running[f"unhome_pb_{i}"] = False

    for i in range(100):
        parent.program_running[f"tool_change_pb_{i}"] = False

    for i in range(1, 10):
        parent.program_running[f"change_cs_{i}"] = False

    for item in AXES:
        parent.program_running[f"touchoff_pb_{item}"] = False
        parent.program_running[f"tool_touchoff_{item}"] = False

    parent.program_running["mdi_s_pb"] = False

    # remove any items not found in the gui
    for item in list(parent.program_running):
        if item not in parent.children:
            del parent.program_running[item]

    parent.program_paused = {
        "run_mdi_pb": False,
        "run_pb": False,
        "run_from_line_pb": False,
        "step_pb": True,
        "pause_pb": False,
        "resume_pb": True,
        "home_all_pb": False,
        "unhome_all_pb": False,
        "actionRun": False,
        "actionRun_From_Line": False,
        "actionStep": True,
        "actionPause": False,
        "actionResume": True,
    }

    for i in range(9):
        parent.program_paused[f"home_pb_{i}"] = False
        parent.program_paused[f"unhome_pb_{i}"] = False

    # remove any items not found in the gui
    for item in list(parent.program_paused):
        if item not in parent.children:
            del parent.program_paused[item]

    # file items if not loaded disable
    file_items = ["edit_pb", "reload_pb", "save_as_pb", "search_pb", "actionEdit", "actionReload", "actionSave_As"]

    parent.file_edit_items = []
    for item in file_items:
        if item in parent.children:
            parent.file_edit_items.append(item)

    if parent.status.file:
        text = open(parent.status.file).read()
        if "gcode_pte" in parent.children:
            parent.gcode_pte.setPlainText(text)
    else:
        for item in parent.file_edit_items:
            getattr(parent, item).setEnabled(False)


def setup_buttons(parent):  # connect buttons to functions
    command_buttons = {
        "abort_pb": "abort",
        "manual_mode_pb": "set_mode_manual",
        "home_all_pb": "home_all",
        "home_pb_0": "home",
        "home_pb_1": "home",
        "home_pb_2": "home",
        "unhome_all_pb": "unhome_all",
        "unhome_pb_0": "unhome",
        "unhome_pb_1": "unhome",
        "unhome_pb_2": "unhome",
        "run_mdi_pb": "run_mdi",
    }

    for key, value in command_buttons.items():
        if key in parent.children:
            getattr(parent, key).clicked.connect(partial(getattr(commands, value), parent))

    action_buttons = {
        "estop_pb": "action_estop",
        "power_pb": "action_power",
        "run_pb": "action_run",
        "run_from_line_pb": "action_run_from_line",
        "step_pb": "action_step",
        "pause_pb": "action_pause",
        "resume_pb": "action_resume",
        "stop_pb": "action_stop",
        "open_pb": "action_open",
        "edit_pb": "action_edit",
        "reload_pb": "action_reload",
        "save_pb": "action_save",
        "save_as_pb": "action_save_as",
        "edit_tool_table_pb": "action_edit_tool_table",
        "edit_ladder_pb": "action_ladder_editor",
        "reload_tool_table_pb": "action_reload_tool_table",
        "quit_pb": "action_quit",
        "clear_mdi_history_pb": "action_clear_mdi",
        "copy_mdi_history_pb": "action_copy_mdi",
        "save_mdi_history_pb": "action_save_mdi",
        "show_hal_pb": "action_show_hal",
        "hal_meter_pb": "action_hal_meter",
        "hal_scope_pb": "action_hal_scope",
        "about_pb": "action_about",
        "quick_reference_pb": "action_quick_reference",
    }

    for key, value in action_buttons.items():
        if key in parent.children:
            getattr(parent, key).clicked.connect(partial(getattr(actions, value), parent))

    if "errors_pte" in parent.children:
        if "clear_errors_pb" in parent.children:
            parent.clear_errors_pb.clicked.connect(partial(utilities.clear_errors, parent))

        if "copy_errors_pb" in parent.children:
            parent.copy_errors_pb.clicked.connect(partial(utilities.copy_errors, parent))

    if "clear_info_pb" in parent.children:
        if "info_pte" in parent.children:
            parent.clear_info_pb.clicked.connect(partial(utilities.clear_info, parent))

    # touch off coordinate system combo box
    if "touchoff_system_cb" in parent.children:
        parent.touchoff_system_cb.setView(QListView())
        coordinate_systems = {"Current": 0, "G54": 1, "G55": 2, "G56": 3, "G57": 4, "G58": 5, "G59": 6, "G59.1": 7, "G59.2": 8, "G59.3": 9}
        for key, value in coordinate_systems.items():
            parent.touchoff_system_cb.addItem(key, value)

    # change coordinate system buttons
    for i in range(1, 10):
        name = f"change_cs_{i}"
        if name in parent.children:
            button = getattr(parent, name)
            button.clicked.connect(partial(commands.change_cs, parent))
            parent.state_estop[name] = False
            parent.state_estop_reset[name] = False
            parent.home_required.append(name)

    # Clear coordinate system buttons
    for i in range(12):
        name = f"clear_coord_{i}"
        if name in parent.children:
            button = getattr(parent, name)
            button.clicked.connect(partial(commands.clear_cs, parent))
            parent.state_estop[name] = False
            parent.state_estop_reset[name] = False
            parent.home_required.append(name)

    checkable_buttons = {
        "flood_pb": "flood_toggle",
        "mist_pb": "mist_toggle",
        "optional_stop_pb": "optional_stop_toggle",
        "block_delete_pb": "block_delete_toggle",
        "feed_override_pb": "feed_override_toggle",
    }
    for key, value in checkable_buttons.items():
        if key in parent.children:  # make sure checkable is set to true
            if not getattr(parent, key).isCheckable():
                getattr(parent, key).setCheckable(True)
            getattr(parent, key).clicked.connect(partial(getattr(commands, value), parent))

    # set the button checked states
    parent.status.poll()
    if "feed_override_pb" in parent.children:
        parent.feed_override_pb.setChecked(parent.status.feed_override_enabled)

    # clear axis offset button setup
    for axis in AXES:
        name = f"clear_{axis}_pb"
        if name in parent.children:
            button = getattr(parent, name)
            button.clicked.connect(partial(commands.clear_axis_offset, parent, axis.upper()))
            parent.state_estop[name] = False
            parent.state_estop_reset[name] = False
            parent.home_required.append(name)

    # override preset buttons
    for item in parent.children:
        if item.startswith("feed_percent_"):
            button = getattr(parent, item)
            button.clicked.connect(partial(commands.feed_override_preset, parent))
        elif item.startswith("rapid_percent_"):
            button = getattr(parent, item)
            button.clicked.connect(partial(commands.rapid_override_preset, parent))
        elif item.startswith("spindle_percent_"):
            button = getattr(parent, item)
            button.clicked.connect(partial(commands.spindle_override_preset, parent))

    # nc code search
    if "search_pb" in parent.children:
        parent.search_pb.clicked.connect(partial(dialogs.find, parent))

    # set button background colors if needed
    if parent.estop_open_color:  # if False just don't bother
        if "estop_pb" in parent.children:
            parent.estop_pb.setStyleSheet(parent.estop_open_color)
        if "flex_E_Stop" in parent.children:
            parent.flex_E_Stop.setStyleSheet(parent.estop_open_color)
    if parent.power_off_color:  # if False just don't bother
        if "power_pb" in parent.children:
            parent.power_pb.setStyleSheet(parent.power_off_color)
        if "flex_Power" in parent.children:
            parent.flex_Power.setStyleSheet(parent.power_off_color)

    # file open buttons
    for child in parent.findChildren(QPushButton):
        if child.property("function") == "load_file":
            child.clicked.connect(partial(actions.load_file, parent))
            # add to enable disables


def setup_menus(parent):
    menus = parent.findChildren(QMenu)
    parent.shortcuts = []
    for menu in menus:
        menu_list = menu.actions()
        for index, action in enumerate(menu_list):
            if action.objectName() == "actionOpen":
                if index + 1 < len(menu_list):
                    parent.menuRecent = QMenu("Recent", parent)
                    parent.menuRecent.setObjectName("menuRecent")
                    parent.children.append("menuRecent")
                    parent.menuFile.insertMenu(menu_list[index + 1], parent.menuRecent)
                    # if any files have been opened add them
                    keys = parent.settings.allKeys()
                    for key in keys:
                        if key.startswith("recent_files"):
                            path = parent.settings.value(key)
                            name = os.path.basename(path)
                            a = parent.menuRecent.addAction(name)
                            a.triggered.connect(partial(getattr(actions, "load_file"), parent, path))
            if action.objectName() == "actionHoming":  # add homing actions
                action.setMenu(QMenu("Homing", parent))

                # add Home All if the home sequence is set for all axes
                if utilities.home_all_check(parent):
                    setattr(parent, "actionHome_All", QAction("Home All", parent))
                    getattr(parent, "actionHome_All").setObjectName("actionHome_all")
                    action.menu().addAction(getattr(parent, "actionHome_All"))
                    getattr(parent, "actionHome_All").triggered.connect(partial(commands.home_all, parent))
                    parent.home_controls.append("actionHome_All")
                    parent.state_estop["actionHome_All"] = False
                    parent.state_estop_reset["actionHome_All"] = False
                    parent.state_on["actionHome_All"] = True
                    parent.program_running["actionHome_All"] = False
                    parent.program_paused["actionHome_All"] = False

                # add Home menu item for each axis
                for i, axis in enumerate(parent.axis_letters):
                    setattr(parent, f"actionHome_{i}", QAction(f"Home {axis}", parent))
                    getattr(parent, f"actionHome_{i}").setObjectName(f"actionHome_{i}")
                    action.menu().addAction(getattr(parent, f"actionHome_{i}"))
                    getattr(parent, f"actionHome_{i}").triggered.connect(partial(commands.home, parent))
                    parent.home_controls.append(f"actionHome_{i}")
                    parent.state_estop[f"actionHome_{i}"] = False
                    parent.state_estop_reset[f"actionHome_{i}"] = False
                    parent.state_on[f"actionHome_{i}"] = True
                    parent.program_running[f"actionHome_{i}"] = False
                    parent.program_paused[f"actionHome_{i}"] = False

            elif action.objectName() == "actionUnhoming":
                action.setMenu(QMenu("Unhoming", parent))
                setattr(parent, "actionUnhome_All", QAction("Unome All", parent))
                getattr(parent, "actionUnhome_All").setObjectName("actionUnhome_All")
                action.menu().addAction(getattr(parent, "actionUnhome_All"))
                getattr(parent, "actionUnhome_All").triggered.connect(partial(commands.unhome_all, parent))
                parent.unhome_controls.append("actionUnhome_All")
                parent.state_estop["actionUnhome_All"] = False
                parent.state_estop_reset["actionUnhome_All"] = False
                parent.state_on["actionUnhome_All"] = True
                parent.program_running["actionUnhome_All"] = False
                parent.program_paused["actionUnhome_All"] = False

                for i, axis in enumerate(parent.axis_letters):
                    setattr(parent, f"actionUnhome_{i}", QAction(f"Unhome {axis}", parent))
                    getattr(parent, f"actionUnhome_{i}").setObjectName(f"actionUnhome_{i}")
                    action.menu().addAction(getattr(parent, f"actionUnhome_{i}"))
                    getattr(parent, f"actionUnhome_{i}").triggered.connect(partial(commands.unhome, parent))
                    parent.unhome_controls.append(f"actionUnhome_{i}")
                    parent.state_estop[f"actionUnhome_{i}"] = False
                    parent.state_estop_reset[f"actionUnhome_{i}"] = False
                    parent.state_on[f"actionUnhome_{i}"] = True
                    parent.program_running[f"actionUnhome_{i}"] = False
                    parent.program_paused[f"actionUnhome_{i}"] = False
            elif action.objectName() == "actionClear_Offsets":
                action.setMenu(QMenu("Clear Offsets", parent))
                cs = ["Current", "G54", "G55", "G56", "G57", "G58", "G59", "G59.1", "G59.2", "G59.3", "G92", "Rotation"]
                for i, item in enumerate(cs):
                    setattr(parent, f"actionClear_{i}", QAction(f"Clear {item}", parent))
                    getattr(parent, f"actionClear_{i}").setObjectName(f"actionClear_{i}")
                    action.menu().addAction(getattr(parent, f"actionClear_{i}"))
                    getattr(parent, f"actionClear_{i}").triggered.connect(partial(commands.clear_cs, parent))

            if len(action.shortcut().toString()) > 0:  # collect shortcuts for quick reference
                parent.shortcuts.append(f"{action.text()}\t{action.shortcut().toString()}")


def setup_actions(parent):  # setup menu actions
    actions_dict = {
        "actionOpen": "action_open",
        "actionEdit": "action_edit",
        "actionReload": "action_reload",
        "actionSave": "action_save",
        "actionSave_As": "action_save_as",
        "actionEdit_Tool_Table": "action_edit_tool_table",
        "actionReload_Tool_Table": "action_reload_tool_table",
        "actionLadder_Editor": "action_ladder_editor",
        "actionQuit": "action_quit",
        "actionE_Stop": "action_estop",
        "actionPower": "action_power",
        "actionRun": "action_run",
        "actionRun_From_Line": "action_run_from_line",
        "actionStep": "action_step",
        "actionPause": "action_pause",
        "actionResume": "action_resume",
        "actionStop": "action_stop",
        "actionClear_MDI_History": "action_clear_mdi",
        "actionCopy_MDI_History": "action_copy_mdi",
        "actionOverlay": "action_toggle_overlay",
        "actionShow_HAL": "action_show_hal",
        "actionHAL_Meter": "action_hal_meter",
        "actionHAL_Scope": "action_hal_scope",
        "actionAbout": "action_about",
        "actionQuick_Reference": "action_quick_reference",
        "actionClear_Live_Plot": "action_clear_live_plot",
    }

    # if an action is found connect it to the function
    for key, value in actions_dict.items():
        if key in parent.children:
            getattr(parent, f"{key}").triggered.connect(partial(getattr(actions, f"{value}"), parent))

    # special check for the classicladder editor
    if not hal.component_exists("classicladder_rt"):
        if "actionLadder_Editor" in parent.children:
            parent.actionLadder_Editor.setEnabled(False)
        if "edit_ladder_pb" in parent.children:
            parent.edit_ladder_pb.setEnabled(False)

    # special check for MDI
    if "mdi_history_lw" in parent.children:
        if "actionClear_MDI_History" in parent.children:
            parent.actionClear_MDI_History.setEnabled(False)
        if "actionCopy_MDI_History" in parent.children:
            parent.actionCopy_MDI_History.setEnabled(False)


def setup_status_labels(parent):
    parent.stat_dict = {
        "adaptive_feed_enabled": {0: False, 1: True},
        "exec_state": {
            1: "EXEC_ERROR",
            2: "EXEC_DONE",
            3: "EXEC_WAITING_FOR_MOTION",
            4: "EXEC_WAITING_FOR_MOTION_QUEUE",
            5: "EXEC_WAITING_FOR_IO",
            7: "EXEC_WAITING_FOR_MOTION_AND_IO",
            8: "EXEC_WAITING_FOR_DELAY",
            9: "EXEC_WAITING_FOR_SYSTEM_CMD",
            10: "EXEC_WAITING_FOR_SPINDLE_ORIENTED",
        },
        "estop": {0: False, 1: True},
        "flood": {0: "OFF", 1: "ON"},
        "mist": {0: "Mist OFF", 1: "Mist ON"},
        "g5x_index": {1: "G54", 2: "G55", 3: "G56", 4: "G57", 5: "G58", 6: "G59", 7: "G59.1", 8: "G59.2", 9: "G59.3"},
        "interp_state": {1: "INTERP_IDLE", 2: "INTERP_READING", 3: "INTERP_PAUSED", 4: "INTERP_WAITING"},
        "interpreter_errcode": {0: "INTERP_OK", 1: "INTERP_EXIT", 2: "INTERP_EXECUTE_FINISH", 3: "INTERP_ENDFILE", 4: "INTERP_FILE_NOT_OPEN", 5: "INTERP_ERROR"},
        "kinematics_type": {1: "KINEMATICS_IDENTITY", 2: "KINEMATICS_FORWARD_ONLY", 3: "KINEMATICS_INVERSE_ONLY", 4: "KINEMATICS_BOTH"},
        "motion_mode": {1: "TRAJ_MODE_FREE", 2: "TRAJ_MODE_COORD", 3: "TRAJ_MODE_TELEOP"},
        "motion_type": {
            0: "MOTION_TYPE_NONE",
            1: "MOTION_TYPE_TRAVERSE",
            2: "MOTION_TYPE_FEED",
            3: "MOTION_TYPE_ARC",
            4: "MOTION_TYPE_TOOLCHANGE",
            5: "MOTION_TYPE_PROBING",
            6: "MOTION_TYPE_INDEXROTARY",
        },
        "program_units": {1: "CANON_UNITS_INCHES", 2: "CANON_UNITS_MM", 3: "CANON_UNITS_CM"},
        "state": {1: "RCS_DONE", 2: "RCS_EXEC", 3: "RCS_ERROR"},
        "task_mode": {
            1: "MODE_MANUAL",
            2: "MODE_AUTO",
            3: "MODE_MDI",
        },
        "task_state": {
            1: "STATE_ESTOP",
            2: "STATE_ESTOP_RESET",
            4: "STATE_ON",
        },
    }

    status_items = [
        "active_queue",
        "actual_position",
        "ain",
        "aout",
        "axis",
        "adaptive_feed_enabled",
        "axis_mask",
        "block_delete",
        "call_level",
        "command",
        "current_line",
        "debug",
        "din",
        "echo_serial_number",
        "enabled",
        "estop",
        "exec_state",
        "feed_hold_enabled",
        "feed_override_enabled",
        "flood",
        "g5x_index",
        "g5x_offset",
        "homed",
        "id",
        "ini_filename",
        "inpos",
        "input_timeout",
        "interp_state",
        "interpreter_errcode",
        "joint",
        "joint_actual_position",
        "joints",
        "kinematics_type",
        "lube",
        "lube_level",
        "mist",
        "motion_line",
        "motion_mode",
        "motion_type",
        "optional_stop",
        "paused",
        "pocket_prepped",
        "probe_tripped",
        "probe_val",
        "probed_position",
        "probing",
        "program_units",
        "queue",
        "queue_full",
        "read_line",
        "settings",
        "spindle",
        "spindles",
        "state",
        "task_mode",
        "task_paused",
        "task_state",
        "tool_in_spindle",
        "tool_from_pocket",
        "tool_offset",
        "tool_table",
    ]

    # check for status labels in the ui key is label and value is status item
    parent.status_labels = {}  # create an empty dictionary
    for item in status_items:  # iterate the status items list
        if f"{item}_lb" in parent.children:  # if the label is found
            parent.status_labels[f"{item}_lb"] = item  # add the status and label

    parent.status_float_labels = {}
    status_float_items = [
        "acceleration",
        "angular_units",
        "current_vel",
        "cycle_time",
        "delay_left",
        "distance_to_go",
        "linear_units",
        "max_acceleration",
        "max_velocity",
        "rapidrate",
        "rotation_xy",
    ]

    for item in status_float_items:  # iterate the status items list
        if f"{item}_lb" in parent.children:  # if the label is found
            p = getattr(parent, f"{item}_lb").property("precision")
            p = p if p is not None else parent.default_precision
            parent.status_float_labels[item] = p  # item & precision

    parent.status_position = {}  # create an empty dictionary
    for i, axis in enumerate(AXES):
        label = f"actual_lb_{axis}"
        if label in parent.children:
            p = getattr(parent, label).property("precision")
            p = p if p is not None else parent.default_precision
            parent.status_position[f"{label}"] = [i, p]  # label , joint & precision

    # DRO labels
    parent.status_dro = {}  # create an empty dictionary
    for i, axis in enumerate(AXES):
        label = f"dro_lb_{axis}"
        if label in parent.children:
            p = getattr(parent, label).property("precision")
            p = p if p is not None else parent.default_precision
            parent.status_dro[f"{label}"] = [i, p]  # add the label, tuple position & precision

    # G5x Offset Labels
    parent.status_g5x_offset = {}  # create an empty dictionary
    for i, axis in enumerate(AXES):
        label = f"g5x_lb_{axis}"
        if label in parent.children:
            p = getattr(parent, label).property("precision")
            p = p if p is not None else parent.default_precision
            parent.status_g5x_offset[f"{label}"] = [i, p]  # add the label, tuple position & precision

    # G92 Offset Labels
    parent.status_g92 = {}  # create an empty dictionary
    for i, axis in enumerate(AXES):
        label = f"g92_lb_{axis}"
        if label in parent.children:
            p = getattr(parent, label).property("precision")
            p = p if p is not None else parent.default_precision
            parent.status_g92[f"{label}"] = [i, p]  # add the label, tuple position & precision

    # Distance to Go Labels
    parent.status_dtg = {}  # create an empty dictionary
    for i, axis in enumerate(AXES):
        label = f"dtg_lb_{axis}"
        if label in parent.children:
            p = getattr(parent, label).property("precision")
            p = p if p is not None else parent.default_precision
            parent.status_dtg[f"{label}"] = [i, p]  # add the label, tuple position & precision

    # check for axis labels in the ui
    # this return a tuple of dictionaries syntax parent.status.axis[0]['velocity']
    # label axis_n_velocity_lb
    parent.status.poll()

    parent.status_axes = {}  # create an empty dictionary
    for i in range(parent.axis_count):
        for item in ["max_position_limit", "min_position_limit", "velocity"]:
            label = f"axis_{i}_{item}_lb"
            if label in parent.children:
                p = getattr(parent, label).property("precision")
                p = p if p is not None else parent.default_precision
                parent.status_axes[label] = [i, item, p]  # axis, status item, precision

    # two joint velocity
    parent.two_vel = {}
    if "two_vel_lb" in parent.children:
        joint_0 = parent.two_vel_lb.property("joint_0")
        joint_1 = parent.two_vel_lb.property("joint_1")
        p = getattr(parent, "two_vel_lb").property("precision")
        p = p if p is not None else parent.default_precision
        if None not in (joint_0, joint_1):  # check for None or False
            parent.two_vel["two_vel_lb"] = [joint_0, joint_1, p]

    # three joint velocity
    parent.three_vel = {}
    if "three_vel_lb" in parent.children:
        joint_0 = parent.three_vel_lb.property("joint_0")
        joint_1 = parent.three_vel_lb.property("joint_1")
        joint_2 = parent.three_vel_lb.property("joint_2")
        p = getattr(parent, "three_vel_lb").property("precision")
        p = p if p is not None else parent.default_precision
        if None not in (joint_0, joint_1, joint_2):  # check for None or False
            parent.three_vel["three_vel_lb"] = [joint_0, joint_1, joint_2, p]

    # check for joint labels in ui
    # these return 16 joints
    joint_items = [
        "backlash",
        "enabled",
        "fault",
        "ferror_current",
        "ferror_highmark",
        "homed",
        "homing",
        "inpos",
        "input",
        "jointType",
        "max_ferror",
        "max_hard_limit",
        "max_position_limit",
        "max_soft_limit",
        "min_ferror",
        "min_hard_limit",
        "min_position_limit",
        "min_soft_limit",
        "output",
        "override_limits",
    ]
    parent.status_joints = {}  # create an empty dictionary
    for i in range(16):
        for item in joint_items:
            if f"joint_{item}_{i}_lb" in parent.children:
                parent.status_joints[f"{item}_{i}"] = f"joint_{item}_{i}_lb"

    # joint velocity joint_velocity_n_lb parent.status.joint[0]['velocity']
    parent.status.poll()
    parent.joint_vel_sec = {}
    for i in range(parent.status.joints):
        if f"joint_vel_sec_{i}_lb" in parent.children:  # if the label is found
            p = getattr(parent, f"joint_vel_sec_{i}_lb").property("precision")
            p = p if p is not None else parent.default_precision
            parent.joint_vel_sec[f"joint_vel_sec_{i}_lb"] = [i, p]  # add the label, tuple position & precision

    parent.joint_vel_min = {}
    for i in range(parent.status.joints):
        if f"joint_vel_min_{i}_lb" in parent.children:  # if the label is found
            p = getattr(parent, f"joint_vel_min_{i}_lb").property("precision")
            p = p if p is not None else parent.default_precision
            parent.joint_vel_min[f"joint_vel_min_{i}_lb"] = [i, p]  # add the label, tuple position & precision

    joint_number_items = ["units", "velocity"]
    parent.status_joint_prec = {}
    for i in range(16):
        for item in joint_number_items:
            if f"joint_{item}_{i}_lb" in parent.children:  # if the label is found
                p = getattr(parent, f"joint_{item}_{i}_lb").property("precision")
                p = p if p is not None else parent.default_precision
                parent.status_joint_prec[f"{item}_{i}"] = [i, p]  # add the label, tuple position & precision

    override_items = {"feed_override_lb": "feedrate", "rapid_override_lb": "rapidrate"}

    parent.overrides = {}
    for label, stat in override_items.items():
        if label in parent.children:
            parent.overrides[label] = stat

    # dio din_0_lb dout_0_lb
    parent.status_dio = {}
    for i in range(64):
        for item in ["din", "dout"]:
            label = f"{item}_{i}_lb"
            if label in parent.children:
                parent.status_dio[label] = [item, i]  # add label and stat
                parent.stat_dict[f"{item}[{i}]"] = {0: False, 1: True}

    # aio ain_0_lb aout_0_lb aio[0] aout[0]
    parent.status_aio = {}
    for i in range(64):
        for item in ["ain", "aout"]:
            label = f"{item}_{i}_lb"
            if label in parent.children:
                p = getattr(parent, f"{item}_{i}_lb").property("precision")
                p = p if p is not None else parent.default_precision
                parent.status_aio[label] = [item, i, p]  # add label, stat and precision

    # check for tool table labels in the ui , 'comment'
    # id and orientation are integers and the rest are floats
    parent.current_tool_intergers = {}
    parent.current_tool_floats = {}
    tool_table_intergers = ["id", "orientation"]
    tool_table_floats = ["xoffset", "yoffset", "zoffset", "aoffset", "boffset", "coffset", "uoffset", "voffset", "woffset", "diameter", "frontangle", "backangle"]

    for item in tool_table_intergers:
        if f"tool_{item}_lb" in parent.children:
            parent.current_tool_intergers[f"tool_{item}_lb"] = item

    for item in tool_table_floats:
        if f"tool_{item}_lb" in parent.children:
            prec = getattr(parent, f"tool_{item}_lb").property("precision")
            prec = prec if prec is not None else parent.default_precision
            parent.current_tool_floats[f"tool_{item}_lb"] = [item, prec]

    parent.current_tool_info = ()

    if "file_lb" in parent.children:
        parent.status.poll()
        gcode_file = parent.status.file or False
        if gcode_file:
            parent.file_lb.setText(os.path.basename(gcode_file))
            if "start_line_lb" in parent.children:
                parent.start_line_lb.setText("0")
        else:
            parent.file_lb.setText("N/A")
            if "start_line_lb" in parent.children:
                parent.start_line_lb.setText("n/a")

    parent.home_status = []
    for i in range(9):
        if f"home_lb_{i}" in parent.children:
            parent.home_status.append(f"home_lb_{i}")

    for item in parent.home_status:
        if parent.status.homed[int(item[-1])]:
            getattr(parent, item).setText("*")
        else:
            getattr(parent, item).setText("")

    if "settings_speed_lb" in parent.children:
        parent.status_settings = {"settings_speed_lb": 2}
        parent.settings_speed_lb.setText(f"S{parent.status.settings[2]}")

    if "mdi_s_pb" in parent.children:
        parent.mdi_s_pb.clicked.connect(partial(commands.spindle, parent))
        parent.home_required.append("mdi_s_pb")


def setup_list_widgets(parent):
    if "file_lw" in parent.children:
        utilities.read_dir(parent)  # this is called from actions as well
        parent.file_lw.itemClicked.connect(partial(actions.file_selector, parent))


def setup_plain_text_edits(parent):
    # for gcode_pte update
    if "gcode_pte" in parent.children:
        parent.gcode_pte.setCenterOnScroll(True)
        parent.gcode_pte.ensureCursorVisible()
        parent.gcode_pte.viewport().installEventFilter(parent)
        parent.gcode_pte.cursorPositionChanged.connect(partial(utilities.update_qcode_pte, parent))
        parent.status.poll()
        parent.last_line = parent.status.motion_line
        parent.gcode_pte.textChanged.connect(partial(utilities.nc_code_changed, parent))


def setup_stacked_widgets(parent):
    children = parent.findChildren(QPushButton)
    for child in children:
        if child.property("change_page"):
            child.clicked.connect(partial(utilities.change_page, parent))
        elif child.property("next_page"):
            child.clicked.connect(partial(utilities.next_page, parent))
        elif child.property("previous_page"):
            child.clicked.connect(partial(utilities.previous_page, parent))


def setup_line_edits(parent):
    parent.number_le = []
    parent.nccode_le = []
    parent.keyboard_le = []
    for child in parent.findChildren(QLineEdit):
        if child.property("input") == "number":  # enable the number pad
            parent.number_le.append(child.objectName())
            child.installEventFilter(parent)
        elif child.property("input") == "nccode":  # enable the nc code pad
            parent.nccode_le.append(child.objectName())
            child.installEventFilter(parent)
        elif child.property("input") == "keyboard":  # enable the keyboard pad
            parent.keyboard_le.append(child.objectName())
            child.installEventFilter(parent)


def setup_spin_boxes(parent):
    parent.touch_sb = []
    for child in parent.findChildren(QAbstractSpinBox):
        if child.property("input") == "number":  # enable the number pad
            sb_child = child.findChild(QLineEdit)
            sb_child.setObjectName(f"{child.objectName()}_child")
            parent.touch_sb.append(sb_child.objectName())
            sb_child.installEventFilter(parent)


def load_postgui(parent):  # load post gui hal and tcl files if found
    if parent.postgui_halfiles:
        for f in parent.postgui_halfiles:
            if os.path.exists(os.path.join(parent.config_path, f)):
                if f.lower().endswith(".tcl"):
                    res = os.spawnvp(os.P_WAIT, "haltcl", ["haltcl", "-i", parent.ini_path, f])
                else:
                    res = os.spawnvp(os.P_WAIT, "halcmd", ["halcmd", "-i", parent.ini_path, "-f", f])
                if res:
                    raise SystemExit(res)
            else:
                msg = f"The POSTGUI_HALFILE\n{os.path.join(parent.config_path, f)}\nwas not found in the configuration directory."
                print(f"Configuration Error: {msg}")


def setup_mdi(parent):
    # mdi_command_le and run_mdi_pb are required to run mdi commands
    # mdi_history_lw is optional
    # parent.mdi_command is tested in status.py so it must exist
    parent.mdi_command = ""

    if "run_mdi_pb" in parent.children:
        if "mdi_command_le" in parent.children:  # we are good to go
            if parent.mdi_command_le.property("input") == "nccode":
                parent.nccode_le.append("mdi_command_le")
                parent.mdi_command_le.installEventFilter(parent)
            elif parent.mdi_command_le.property("input") == "keyboard":
                parent.keyboard_le.append("mdi_command_le")
                parent.mdi_command_le.installEventFilter(parent)
            else:  # keyboard and mouse
                parent.mdi_command_le.returnPressed.connect(partial(commands.run_mdi, parent))
            parent.home_required.append("run_mdi_pb")
        else:  # missing mdi_command_le
            parent.run_mdi_pb.setEnabled(False)

    if "mdi_history_lw" in parent.children:
        path = os.path.dirname(parent.status.ini_filename)
        mdi_file = os.path.join(path, "mdi_history.txt")
        if os.path.exists(mdi_file):  # load mdi history
            with open(mdi_file, "r") as f:
                history_list = f.readlines()
                for item in history_list:
                    parent.mdi_history_lw.addItem(item.strip())
        parent.mdi_history_lw.itemSelectionChanged.connect(partial(utilities.add_mdi, parent))


def setup_jog(parent):
    # keyboard jog
    if "keyboard_jog_cb" in parent.children:
        parent.keyboard_jog_cb.toggled.connect(partial(utilities.jog_toggled, parent))
        if parent.keyboard_jog_cb.isChecked():
            parent.enable_kb_jogging = True
        else:
            parent.enable_kb_jogging = False

    required_jog_items = ["jog_vel_sl", "jog_modes_cb"]
    parent.jog_buttons = []
    for i in range(16):
        if f"jog_plus_pb_{i}" in parent.children:
            parent.jog_buttons.append(f"jog_plus_pb_{i}")
        if f"jog_minus_pb_{i}" in parent.children:
            parent.jog_buttons.append(f"jog_minus_pb_{i}")

    if len(parent.jog_buttons) > 0:
        for item in required_jog_items:
            # don't make the connection if all required widgets are not present
            if item not in parent.children:
                msg = f"{item} is required to jog\n but was not found.\nJog Buttons will be disabled."
                print(f"Missing Item: {msg}")
                for item in parent.jog_buttons:
                    getattr(parent, item).setEnabled(False)
                return

        # ok to connect if we get this far
        for item in parent.jog_buttons:  # connect jog buttons
            getattr(parent, item).pressed.connect(partial(getattr(commands, "jog"), parent))
            getattr(parent, item).released.connect(partial(getattr(commands, "jog"), parent))
            parent.state_estop[item] = False
            parent.state_estop_reset[item] = False
            parent.state_on[item] = True
            parent.program_running[item] = False

    if "jog_vel_sl" in parent.children:
        min_jog_vel = parent.inifile.find("DISPLAY", "MIN_LINEAR_VELOCITY") or False

        if float(min_jog_vel) > 0:
            int_min_jog_vel = int(float(min_jog_vel) * 60)
            parent.jog_vel_sl.setMinimum(int_min_jog_vel)
            if int_min_jog_vel == 0:
                msg = (
                    "The [DISPLAY] MIN_LINEAR_VELOCITY\n"
                    f"setting is {float(min_jog_vel)} units per second.\n"
                    f"Calculating for units per minute {float(min_jog_vel)} x 60 = {float(min_jog_vel) * 60}\n"
                    "results in less than 1 unit per minute.\n"
                    "The jog slider uses integers only so it will be set to 0."
                )
                print(f"INI Configuration: {msg}")

        # FIXME move to read_ini.py
        max_jog_vel = parent.inifile.find("TRAJ", "MAX_LINEAR_VELOCITY") or False
        if max_jog_vel:
            parent.jog_vel_sl.setMaximum(int(float(max_jog_vel) * 60))

        # FIXME move to read_ini.py
        default_vel = parent.inifile.find("DISPLAY", "DEFAULT_LINEAR_VELOCITY") or False
        if default_vel:
            parent.jog_vel_sl.setValue(int(float(default_vel) * 60))

        if "min_jog_vel_lb" in parent.children:
            if min_jog_vel:
                parent.min_jog_vel_lb.setText(f"{int(float(min_jog_vel) * 60)}")
        if "max_jog_vel_lb" in parent.children:
            if max_jog_vel:
                parent.max_jog_vel_lb.setText(f"{int(float(max_jog_vel) * 60)}")

        if "jog_vel_lb" in parent.children:
            parent.jog_vel_sl.valueChanged.connect(partial(utilities.update_jog_lb, parent))
            parent.jog_vel_lb.setText(f"{parent.jog_vel_sl.value()}")
            utilities.update_jog_lb(parent)

        # machine units are inch
        # do not convert in or inch
        # convert mil to inch mil * 0.001 = inch
        # convert cm to inch divide the value by 2.54
        # convert mm to inch divide the value by 25.4
        # convert um to inch divide the value by 25400

        # machine units are mm
        # convert inches to mm multiply the value by 25.4
        # convert mil to mm mil * 0.001 = inch multiply the value by 25.4
        # convert cm to mm multiply the length value by 10
        # no conversion for mm
        # convert um to mm divide the length value by 1000

        parent.jog_modes_cb.setView(QListView())
        parent.jog_modes_cb.addItem("Continuous", False)

        # FIXME move to read_ini.py
        machine_units = parent.inifile.find("TRAJ", "LINEAR_UNITS") or False
        units = ["mm", "cm", "um", "in", "inch", "mil"]
        # FIXME move to read_ini.py
        increments = parent.inifile.find("DISPLAY", "INCREMENTS") or False

        if increments:
            incr_list = []
            values = increments.split(",")
            for item in values:
                item = item.strip()
                if item[-1].isdigit():
                    distance = conv_to_decimal(item)  # if it's a fraction convert to decimal
                    incr_list.append([item, distance])
                    parent.jog_modes_cb.addItem(item, distance)
                else:
                    for suffix in units:
                        if item.endswith(suffix):
                            distance = item.removesuffix(suffix).strip()
                            if utilities.is_float(distance):
                                converted_distance = conv_units(distance, suffix, machine_units)
                                incr_list.append([item, converted_distance])
                                parent.jog_modes_cb.addItem(item, converted_distance)
                                break
                            else:
                                msg = f"Malformed INCREMENTS value\n{distance}\nmay be missing comma seperators?"
                                print(f"Error: {msg}")
                    else:
                        msg = f"INI section DISPLAY value INCREMENTS\n{item} is not a valid jog increment\nand will not be added to the jog options."
                        print(f"Configuration Error: {msg}")


def setup_jog_selected(parent):
    parent.axes_group = QButtonGroup()
    for i in range(9):
        if f"axis_select_{i}" in parent.children:
            parent.axes_group.addButton(getattr(parent, f"axis_select_{i}"))
    if len(parent.axes_group.buttons()) > 0:
        parent.axes_group.buttons()[0].setChecked(True)
        if "jog_selected_plus" in parent.children:
            parent.jog_selected_plus.pressed.connect(partial(commands.jog_selected, parent))
            parent.jog_selected_plus.released.connect(partial(commands.jog_selected, parent))
        if "jog_selected_minus" in parent.children:
            parent.jog_selected_minus.pressed.connect(partial(commands.jog_selected, parent))
            parent.jog_selected_minus.released.connect(partial(commands.jog_selected, parent))


def conv_units(value, suffix, machine_units):
    if machine_units == "inch":
        if suffix == "in" or suffix == "inch":
            return float(value)
        elif suffix == "mil":
            return float(value) * 0.001
        elif suffix == "cm":
            return float(value) / 2.54
        elif suffix == "mm":
            return float(value) / 25.4
        elif suffix == "um":
            return float(value) / 25400

    elif machine_units == "mm":
        if suffix == "in" or suffix == "inch":
            return float(value) * 25.4
        elif suffix == "mil":
            return float(value) * 0.0254
        elif suffix == "cm":
            return float(value) * 10
        elif suffix == "mm":
            return float(value)
        elif suffix == "um":
            return float(value) / 1000


def conv_to_decimal(data):
    if "/" in data:
        p, q = data.split("/")
        return float(p) / float(q)
    else:
        return float(data)


def setup_spindle(parent):
    # spindle defaults
    # FIXME move to read_ini.py
    default_rpm = parent.inifile.find("DISPLAY", "DEFAULT_SPINDLE_SPEED") or False
    if default_rpm:
        parent.spindle_speed = int(default_rpm)
    else:
        parent.spindle_speed = 0
    if "spindle_speed_lb" in parent.children:
        parent.spindle_speed_lb.setText(f"{parent.spindle_speed}")
    parent.min_rpm = 0

    spindle_buttons = {
        "spindle_fwd_pb": "spindle",
        "spindle_rev_pb": "spindle",
        "spindle_stop_pb": "spindle",
        "spindle_plus_pb": "spindle",
        "spindle_minus_pb": "spindle",
    }
    for key, value in spindle_buttons.items():
        if key in parent.children:
            getattr(parent, key).clicked.connect(partial(getattr(commands, value), parent))
            if key in ["spindle_fwd_pb", "spindle_rev_pb"]:
                getattr(parent, key).setCheckable(True)

    if parent.min_rpm and utilities.is_number(parent.min_rpm):
        parent.min_rpm = int(parent.min_rpm)
    else:
        parent.min_rpm = 0

    if parent.max_rpm and utilities.is_number(parent.max_rpm):
        parent.max_rpm = int(parent.max_rpm)
    else:
        parent.max_rpm = 1000

    if "spindle_speed_sb" in parent.children:
        parent.spindle_speed_sb.valueChanged.connect(partial(commands.spindle, parent))
        parent.spindle_speed_sb.setValue(parent.spindle_speed)
        parent.spindle_speed_sb.setSingleStep(parent.increment)
        parent.spindle_speed_sb.setMinimum(parent.min_rpm)
        parent.spindle_speed_sb.setMaximum(parent.max_rpm)

    if "spindle_speed_setting_lb" in parent.children:
        parent.spindle_speed_setting_lb.setText(f"{parent.min_rpm}")

    if "spindle_override_sl" in parent.children:
        parent.spindle_override_sl.valueChanged.connect(partial(utilities.spindle_override, parent))
        # FIXME move to read_ini.py
        max_spindle_override = parent.inifile.find("DISPLAY", "MAX_SPINDLE_OVERRIDE") or False
        if not max_spindle_override:
            max_spindle_override = 1.0
        max_spindle_override = int(float(max_spindle_override) * 100)
        parent.spindle_override_sl.setMaximum(max_spindle_override)
        if max_spindle_override >= 100:
            parent.spindle_override_sl.setValue(100)

    # check for spindle labels in the ui
    spindle_items = ["brake", "direction", "enabled", "homed", "orient_fault", "orient_state", "override", "override_enabled"]
    parent.status_spindles = {}
    parent.status_spindle_overrides = {}
    parent.status_spindle_lcd = {}
    parent.status.poll()

    # only look for the num of spindles configured
    for i in range(parent.status.spindles):
        for item in spindle_items:
            if f"spindle_{item}_{i}_lb" in parent.children:
                parent.status_spindles[f"spindle_{item}_{i}_lb"] = item

        if f"spindle_override_{i}_lb" in parent.children:
            parent.status_spindle_overrides[f"spindle_override_{i}_lb"] = i

    # FIXME might think about this a bit...
    parent.status_spindle_dir = {}
    if "spindle_direction_0_lb" in parent.children:
        parent.status_spindle_dir["spindle_direction_0_lb"] = ["direction"]

    parent.status_spindle_speed = {}
    if "spindle_speed_0_lb" in parent.children:
        parent.status_spindle_speed["spindle_speed_0_lb"] = "speed"

    if "spindle_speed_0_lcd" in parent.children:
        parent.status_spindle_lcd["spindle_speed_0_lcd"] = "speed"

    # special spindle labels
    parent.spindle_actual_speed = []
    # only add the actual speed if the override slider is there
    spindle_actual_speed = ["spindle_actual_speed_lb", "spindle_override_sl"]
    if all(x in parent.children for x in spindle_actual_speed):
        parent.spindle_actual_speed.append("spindle_actual_speed_lb")


def setup_touchoff(parent):
    # check for required items tool_touchoff_ touchoff_pb_
    if "touchoff_le" in parent.children:
        parent.touchoff_le.setText("0")
        if parent.touchoff_le.property("input") == "number":  # enable the number pad
            parent.touchoff_le.installEventFilter(parent)
            parent.number_le.append("touchoff_le")

    # setup touch off buttons
    for axis in AXES:
        item = f"touchoff_pb_{axis}"
        if item in parent.children:
            source = getattr(parent, item).property("source")
            if source is None:
                if "touchoff_le" in parent.children:  # check for touchoff_le
                    getattr(parent, item).clicked.connect(partial(getattr(commands, "touchoff"), parent))
                    parent.home_required.append(item)
                else:
                    getattr(parent, item).setEnabled(False)
                    msg = "The Touchoff Button requires\nthe Offset Line Edit touchoff_le\nor a Dynamic Property named source that\nhas the name of the QLineEdit to be used."
                    print(f"Required Item Missing: {msg}")
            else:  # property source is found
                if source in parent.children:
                    getattr(parent, item).clicked.connect(partial(getattr(commands, "touchoff"), parent))
                    parent.home_required.append(item)
                else:  # the source was not found
                    msg = f"The {source} for {item}\nwas not found. The QPushButton\n{item} will be disabled."
                    print(f"Required Item Missing: {msg}")

    # setup Axis style touch off buttons
    if "touchoff_selected_pb" in parent.children:
        for i in range(9):
            if f"axis_select_{i}" in parent.children:
                parent.touchoff_selected_pb.clicked.connect(partial(dialogs.touchoff_selected, parent))
                break


def setup_tools(parent):
    parent.tool_changed = False
    # tool change using a combo box
    tool_change_required = ["tool_change_pb", "tool_change_cb"]
    # test to see if any tool change items are in the ui
    if set(tool_change_required) & set(parent.children):
        # test to make sure all items required are in the ui
        if not all(item in parent.children for item in tool_change_required):
            missing_items = list(sorted(set(tool_change_required) - set(parent.children)))
            missing = " ".join(missing_items)
            msg = f"Tool change requires both\nthe tool_change_cb combo box\nand the tool_change_pb push button.\n{missing} was not found."
            print(f"Required Item Missing: {msg}")
            return
        parent.tool_change_pb.clicked.connect(partial(commands.tool_change, parent))
        parent.home_required.append("tool_change_pb")
        parent.tool_change_cb.setView(QListView())

        # tool change with description
        if parent.tool_change_cb.property("option") == "description":
            parent.tool_change_cb.addItem("T0: No Tool in Spindle", 0)
            tools = os.path.join(parent.config_path, parent.tool_table)
            with open(tools, "r") as t:
                tool_list = t.readlines()
            for line in tool_list:
                if line.find("T") >= 0:
                    t = line.find("T")
                    p = line.find("P")
                    tool = line[t:p].strip()
                    desc = line.split(";")[-1]
                    number = int(line[t + 1 : p].strip())
                    parent.tool_change_cb.addItem(f"{tool} {desc.strip()}", number)

        elif parent.tool_change_cb.property("prefix") is not None:
            prefix = parent.tool_change_cb.property("prefix")
            tool_len = len(parent.status.tool_table)
            parent.tool_change_cb.addItem(f"{prefix} 0", 0)
            for i in range(1, tool_len):
                tool_id = parent.status.tool_table[i][0]
                parent.tool_change_cb.addItem(f"{prefix} {tool_id}", tool_id)

        else:
            tool_len = len(parent.status.tool_table)
            parent.tool_change_cb.addItem("Tool 0", 0)
            for i in range(1, tool_len):
                tool_id = parent.status.tool_table[i][0]
                parent.tool_change_cb.addItem(f"Tool {tool_id}", tool_id)

    # tool change push buttons is a MDI command so power on and all homed
    parent.tool_button = False
    for i in range(100):
        item = f"tool_change_pb_{i}"
        if item in parent.children:
            getattr(parent, item).clicked.connect(partial(commands.tool_change, parent))
            parent.home_required.append(item)

    if "tool_changed_pb" in parent.children:
        parent.tool_changed_pb.setEnabled(False)
        parent.tool_changed_pb.clicked.connect(partial(commands.tool_changed, parent))

    if "tool_touchoff_le" in parent.children:
        parent.tool_touchoff_le.setText("0")
        if parent.tool_touchoff_le.property("input") == "number":  # enable the number pad
            parent.tool_touchoff_le.installEventFilter(parent)
            parent.number_le.append("tool_touchoff_le")

    for axis in AXES:
        item = f"tool_touchoff_{axis}"
        if item in parent.children:
            source = getattr(parent, item).property("source")
            if source is None:  # check for tool_touchoff_le
                if "tool_touchoff_le" in parent.children:
                    getattr(parent, item).clicked.connect(partial(getattr(commands, "tool_touchoff"), parent))
                    parent.home_required.append(item)
                else:
                    getattr(parent, item).setEnabled(False)
                    msg = "Tool Touchoff Button requires\nthe Tool Offset Line Edit tool_touchoff_le\nor a Dynamic Property named source that\nhas the name of the QLineEdit to be used."
                    print(f"Required Item Missing: {msg}")
            else:  # property source is found
                if source in parent.children:
                    getattr(parent, item).clicked.connect(partial(getattr(commands, "tool_touchoff"), parent))
                    parent.home_required.append(item)
                else:  # the source was not found
                    msg = f"The {source} for {item}\nwas not found. The QPushButton\n{item} will be disabled."
                    print(f"Source Name Error: {msg}")

    # Axis style tool touch off
    if "tool_touchoff_selected_pb" in parent.children:
        parent.tool_touchoff_selected_pb.clicked.connect(partial(dialogs.tool_touchoff_selected, parent))


def setup_sliders(parent):
    if "feed_override_sl" in parent.children:
        parent.feed_override_sl.valueChanged.connect(partial(utilities.feed_override, parent))
        # FIXME move to read_ini.py
        max_feed_override = parent.inifile.find("DISPLAY", "MAX_FEED_OVERRIDE") or False
        if not max_feed_override:
            max_feed_override = 1.0
        parent.feed_override_sl.setMaximum(int(float(max_feed_override) * 100))
        parent.feed_override_sl.setValue(100)

    if "rapid_override_sl" in parent.children:
        parent.rapid_override_sl.valueChanged.connect(partial(utilities.rapid_override, parent))
        parent.rapid_override_sl.setMaximum(100)
        parent.rapid_override_sl.setValue(100)

    if "max_vel_sl" in parent.children:
        parent.max_vel_sl.valueChanged.connect(partial(utilities.max_velocity, parent))
        max_units_min = int(float(parent.max_linear_vel) * 60)
        parent.max_vel_sl.setMaximum(max_units_min)
        parent.max_vel_sl.setValue(max_units_min)


def setup_overrides(parent):
    if "override_limits_cb" in parent.children:
        parent.override_limits_cb.setEnabled(False)


def setup_defaults(parent):
    if "optional_stop_pb" in parent.children:
        if parent.optional_stop_pb.isChecked():
            parent.command.set_optional_stop(True)
        else:
            parent.command.set_optional_stop(False)

    # FIXME move to read_ini.py
    open_file = parent.inifile.find("DISPLAY", "OPEN_FILE") or False
    if open_file and open_file != '""':
        actions.load_file(parent, open_file)


def setup_probing(parent):
    # any object name that starts with probe_ is disabled
    # print('setup_probing')
    parent.probing = False
    parent.probe_controls = []
    for child in parent.children:
        if child.startswith("probe_") and not isinstance(child, QLabel):
            if not isinstance(parent.findChild(QWidget, child), QLabel):
                getattr(parent, child).setEnabled(False)
                parent.probe_controls.append(child)
    if len(parent.probe_controls) > 0:  # make sure the probe enable is present
        if "probing_enable_pb" in parent.children:
            parent.state_estop["probing_enable_pb"] = False
            parent.state_estop_reset["probing_enable_pb"] = False
            parent.state_estop_checked["probing_enable_pb"] = False
            parent.state_estop_reset_checked["probing_enable_pb"] = False

            parent.probing_enable_pb.setCheckable(True)
            parent.home_required.append("probing_enable_pb")
            parent.probing_enable_pb.toggled.connect(partial(probe.toggle, parent))
            on_text = parent.probing_enable_pb.property("on_text")
            off_text = parent.probing_enable_pb.property("off_text")
            if None not in [on_text, off_text]:
                parent.probing_enable_pb.setText(off_text)
            if parent.probe_enable_off_color:
                parent.probing_enable_pb.setStyleSheet(parent.probe_enable_off_color)

        else:
            msg = "The Probing Enable Push Button\nwas not found, all probe controls\nwill be disabled. Did you name it\nprobing_enable_pb?"
            print(f"Object Not Found: {msg}")
    else:  # no prob controls found
        if "probing_enable_pb" in parent.children:
            msg = "The Probing Enable Push Button\nwas found, but no probe controls\nwere found. The button will be set\nto disabled."
            print(f"Configuration Error: {msg}")
            parent.probing_enable_pb.setEnabled(False)


def setup_mdi_buttons(parent):
    for button in parent.findChildren(QAbstractButton):
        if button.property("function") == "mdi":
            if button.property("command"):
                button_name = button.objectName()
                button.clicked.connect(partial(commands.mdi_button, parent, button))
                # probe buttons are taken care of in setup_probe function
                if button_name.startswith("probe_"):
                    parent.probe_controls.append(button_name)
                else:
                    parent.program_running[button_name] = False
                    parent.state_estop[button_name] = False
                    parent.home_required.append(button_name)
            else:
                msg = f"MDI Button {button.text()}\nDoes not have a command\n{button.text()} will not be functional."
                print(f"Configuration Error: {msg}")
                button.setEnabled(False)


def setup_set_var(parent):
    # variables are floats so only put them in a QDoubleSpinBox
    var_file = os.path.join(parent.config_path, parent.var_file)
    with open(var_file, "r") as f:
        var_list = f.readlines()

    parent.set_var = {}
    for child in parent.findChildren(QDoubleSpinBox):
        prop = child.property("function")
        if prop == "set_var":
            var = child.property("variable")
            found = False
            if var is not None:
                for line in var_list:
                    if line.startswith(var):
                        child.setValue(float(line.split()[1]))
                        found = True
                        child.valueChanged.connect(partial(utilities.var_value_changed, parent))
                        parent.set_var[child.objectName()] = var
                        child.setEnabled(False)
                        parent.home_required.append(child.objectName())
                        break
                if not found:
                    msg = f"The variable {var} was not found\nin the variables file {parent.var_file}\nthe QDoubleSpinBox {child.objectName()}\nwill not contain any value."
                    print(f"Error: {msg}")


def setup_watch_var(parent):
    parent.watch_var = {}
    for child in parent.findChildren(QLabel):
        if child.property("function") == "watch_var":
            var = child.property("variable")
            prec = child.property("precision")
            prec = prec if prec is not None else 6
            name = child.objectName()
            parent.watch_var[name] = [var, prec]

    if len(parent.watch_var) > 0:  # update the labels
        var_file = os.path.join(parent.config_path, parent.var_file)
        with open(var_file, "r") as f:
            var_list = f.readlines()
        for key, value in parent.watch_var.items():
            for line in var_list:
                if line.startswith(value[0]):
                    getattr(parent, key).setText(f"{float(line.split()[1]):.{value[1]}f}")


class CustomWidgets:
    def paintEventLED(self, event):
        self._diameter = 10
        painter = QPainter(self)
        size = self.rect()
        x_center = size.width() / 2
        y_center = size.height() / 2
        x = size.width() - self._diameter
        y = size.height() - self._diameter
        gradient = QRadialGradient(x + self._diameter / 2, y + self._diameter / 2, self._diameter * 0.4, self._diameter * 0.4, self._diameter * 0.4)
        gradient.setColorAt(0, Qt.GlobalColor.white)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        if isinstance(self.led_color, str) and hasattr(Qt.GlobalColor, self.led_color):
            gradient.setColorAt(1, getattr(Qt.GlobalColor, self.led_color))
        else:
            gradient.setColorAt(1, Qt.GlobalColor.black)
        painter.setBrush(QBrush(gradient))
        painter.setPen(Qt.GlobalColor.black)
        painter.drawEllipse(QPointF(x_center, y_center), self._diameter / 2, self._diameter / 2)

    def addValueGraph(self, value):
        # TODO: limiting update interval
        self.history.append(value)
        self.history = self.history[-(self.history_max + 1) :]
        self.setText(str(value))

    def paintEventGraph(self, event):
        self.graph = True
        painter = QPainter(self)
        size = self.rect()
        width = size.width()
        height = size.height()

        # painter.setPen(Qt.GlobalColor.gray)
        # for n in range(0, 100, 10):
        #    y = height - n
        #    painter.drawLine(0, int(y), width, int(y))

        painter.setPen(Qt.GlobalColor.black)
        painter.drawRect(0, 0, width - 1, height - 1)

        painter.setPen(Qt.GlobalColor.red)
        gwidth = width - 2
        gheight = height - 2
        x_last = 1
        y_last = gheight - (gheight / self.vmax * self.history[0]) + 1
        for vn, value in enumerate(self.history):
            x = gwidth / self.history_max * vn + 1
            y = gheight - (gheight / self.vmax * value) + 1
            painter.drawLine(int(x_last), int(y_last), int(x), int(y))
            x_last = x
            y_last = y


def setup_hal(parent):
    hal_labels = []
    hal_ms_labels = []  # multi state labels
    hal_buttons = []
    hal_spinboxes = []
    hal_sliders = []
    hal_lcds = []
    hal_leds = []
    hal_progressbar = []
    parent.hal_io = {}
    parent.hal_readers = {}
    parent.hal_ms_labels = {}
    parent.hal_bool_labels = {}
    parent.hal_progressbars = {}
    parent.hal_floats = {}
    parent.hal_history = []
    children = parent.findChildren(QWidget)

    var_file = os.path.join(parent.config_path, parent.var_file)
    with open(var_file, "r") as f:
        var_list = f.readlines()

    ##### HAL_IO #####

    for child in children:
        if child.property("function") == "hal_io":
            child_name = child.objectName()
            pin_name = child.property("pin_name")
            hal_type = child.property("hal_type")
            hal_dir = child.property("hal_dir")
            hal_type = getattr(hal, f"{hal_type}")
            hal_dir = getattr(hal, f"{hal_dir}")
            setattr(parent, f"{pin_name}", parent.halcomp.newpin(pin_name, hal_type, hal_dir))

            if isinstance(child, QCheckBox):
                if hal_type == hal.HAL_BIT:
                    child.stateChanged.connect(partial(utilities.update_hal_io, parent))
                else:
                    msg = f"The {child_name} has a hal_type of {hal_type}\nOnly a hal_type of HAL_BIT can be used with\na QCheckBox"
                    print(f"Error: {msg}")
            elif isinstance(child, QPushButton):
                if hal_type == hal.HAL_BIT:
                    if child.isCheckable():
                        child.toggled.connect(partial(utilities.update_hal_io, parent))
                    else:
                        msg = f"The QPushButton {child_name} must be\nset to checkable to be a IO button."
                        print(f"Error: {msg}")
                else:
                    msg = "The QPushButton hal_type must be\nset to hal.HAL_BIT."
                    print(f"Error: {msg}")
            elif isinstance(child, QRadioButton):
                if hal_type == hal.HAL_BIT:
                    child.toggled.connect(partial(utilities.update_hal_io, parent))
                else:
                    msg = "The QRadioButton hal_type must be\nset to hal.HAL_BIT."
                    print(f"Error: {msg}")
            elif isinstance(child, QSpinBox):
                if hal_type in [hal.HAL_S32, hal.HAL_U32]:
                    child.valueChanged.connect(partial(utilities.update_hal_io, parent))
                else:
                    msg = "The QSpinBox hal_type must be\nset to hal.HAL_S32 or hal.HAL_U32."
                    print(f"Error: {msg}")
            elif isinstance(child, QDoubleSpinBox):
                if hal_type == hal.HAL_FLOAT:
                    child.valueChanged.connect(partial(utilities.update_hal_io, parent))
                else:
                    msg = "The QDoubleSpinBox hal_type must be\nset to hal.HAL_FLOAT."
                    print(f"Error: {msg}")
            elif isinstance(child, QSlider):
                if hal_type in [hal.HAL_S32, hal.HAL_U32, hal.HAL_FLOAT]:
                    child.valueChanged.connect(partial(utilities.update_hal_io, parent))
                else:
                    msg = "The QSlider hal_type must be\nset to hal.HAL_S32 or hal.HAL_U32 or hal.HAL_FLOAT."
                    print(f"Error: {msg}")

            parent.hal_io[child_name] = pin_name

            if child.property("variable") is not None:
                var = child.property("variable")
                found = False
                for line in var_list:
                    if line.startswith(var):
                        child.setValue(float(line.split()[1]))
                        found = True
                        break
                if not found:
                    msg = f"The variable {var} was not found\nin the variables file {parent.var_file}\nthe QDoubleSpinBox {child.objectName()}\nwill not contain any value."
                    print(f"Error: {msg}")

    for child in children:
        if child.property("function") == "hal_pin":
            if isinstance(child, QAbstractButton):  # QCheckBox, QPushButton, QRadioButton, and QToolButton
                hal_buttons.append(child)
            elif isinstance(child, QAbstractSpinBox):  # QDateTimeEdit, QDoubleSpinBox, and QSpinBox
                hal_spinboxes.append(child)
            elif isinstance(child, QSlider):
                hal_sliders.append(child)
            elif isinstance(child, QLabel):
                if child.property("true_color"):
                    child.led_color = Qt.GlobalColor.black
                    child.paintEvent = partial(CustomWidgets.paintEventLED, child)
                elif child.property("history"):
                    child.paintEvent = partial(CustomWidgets.paintEventGraph, child)
                    child.addValue = partial(CustomWidgets.addValueGraph, child)
                    child.history_max = int(child.property("history"))
                    child.vmin = float(child.property("min"))
                    child.vmax = float(child.property("max"))
                    child.history = []
                hal_labels.append(child)
                parent.hal_history.append(child)
            elif isinstance(child, QProgressBar):
                hal_progressbar.append(child)
            elif isinstance(child, QLCDNumber):
                hal_lcds.append(child)
        elif child.property("function") == "hal_led":
            if isinstance(child, QLabel):
                hal_leds.append(child)
        elif child.property("function") == "hal_msl":
            if isinstance(child, QLabel):
                hal_ms_labels.append(child)

    if len(hal_lcds) > 0:  # setup hal labels
        valid_types = ["HAL_FLOAT", "HAL_S32", "HAL_U32"]
        for lcd in hal_lcds:
            lcd_name = lcd.objectName()
            pin_name = lcd.property("pin_name")
            if pin_name in dir(parent):
                msg = f"HAL LCD {lcd_name}\npin name {pin_name}\nis already used in Flex GUI\nThe HAL pin can not be created."
                print(f"Configuration Error: {msg}")
                continue

            hal_type = lcd.property("hal_type")
            if hal_type not in valid_types:
                lcd.setEnabled(False)
                msg = f"{hal_type} is not valid\nfor a HAL LCD, only\nHAL_FLOAT or HAL_S32 or HAL_U32\ncan be used. The {lcd_name} will be disabled."
                print(f"Configuration Error: {msg}")
                continue

            hal_dir = lcd.property("hal_dir")
            if hal_dir != "HAL_IN":
                lcd.setEnabled(False)
                msg = f"{hal_dir} is not a valid\nhal_dir for a HAL LCD Display,\nonly HAL_IN can be used for hal_dir.\nThe {lcd_name} LCD will be disabled."
                print(f"Configuration Error: {msg}")
                continue

            if lcd_name == pin_name:
                lcd.setEnabled(False)
                msg = f"The object name {lcd_name}\ncan not be the same as the\npin name {pin_name}.\nThe HAL object will not be created\nand the LCD will be disabled."
                print(f"Configuration Error: {msg}")
                continue

            if None not in [pin_name, hal_type, hal_dir]:
                hal_type = getattr(hal, f"{hal_type}")
                hal_dir = getattr(hal, f"{hal_dir}")
                setattr(parent, f"{pin_name}", parent.halcomp.newpin(pin_name, hal_type, hal_dir))
                pin = getattr(parent, f"{pin_name}")
                # if hal type is float add it to hal_float with precision
                if hal_type == 2:  # HAL_FLOAT
                    p = lcd.property("precision")
                    p = p if p is not None else parent.default_precision
                    parent.hal_floats[f"{lcd_name}"] = [pin_name, p]  # lcd ,status item, precision
                else:
                    parent.hal_readers[lcd_name] = pin_name

    if len(hal_labels) > 0:  # setup hal labels
        valid_types = ["HAL_BIT", "HAL_FLOAT", "HAL_S32", "HAL_U32"]
        for label in hal_labels:
            label_name = label.objectName()
            pin_name = label.property("pin_name")
            true_text = label.property("true_text")
            false_text = label.property("false_text")
            true_color = label.property("true_color")
            false_color = label.property("false_color")
            if pin_name in dir(parent):
                msg = f"HAL Label {label_name}\npin name {pin_name}\nis already used in Flex GUI\nThe HAL pin can not be created."
                print(f"Configuration Error: {msg}")
                continue

            hal_type = label.property("hal_type")
            if hal_type not in valid_types:
                label.setEnabled(False)
                msg = f"{hal_type} is not valid for a HAL Label\n, only HAL_BIT, HAL_FLOAT, HAL_S32 or HAL_U32\ncan be used. The {label_name} label will be disabled."
                print(f"Configuration Error: {msg}")
                continue

            hal_dir = label.property("hal_dir")
            if hal_dir != "HAL_IN":
                label.setEnabled(False)
                msg = f"{hal_dir} is not a valid\nhal_dir for a HAL Lable,\nonly HAL_IN can be used for hal_dir.\nThe {label_name} Label will be disabled."
                print(f"Configuration Error: {msg}")
                continue

            if label_name == pin_name:
                label.setEnabled(False)
                msg = f"The object name {label_name}\ncan not be the same as the\npin name {pin_name}.\nThe HAL object will not be created\nand the label will be disabled."
                print(f"Configuration Error: {msg}")
                continue

            if None not in [pin_name, hal_type, hal_dir]:
                hal_type = getattr(hal, f"{hal_type}")
                hal_dir = getattr(hal, f"{hal_dir}")
                setattr(parent, f"{pin_name}", parent.halcomp.newpin(pin_name, hal_type, hal_dir))
                pin = getattr(parent, f"{pin_name}")
                # if hal type is float add it to hal_float with precision
                if hal_type == 2:  # HAL_FLOAT
                    p = label.property("precision")
                    p = p if p is not None else parent.default_precision
                    parent.hal_floats[f"{label_name}"] = [pin_name, p]  # label ,status item, precision
                elif true_color and false_color:
                    parent.hal_bool_labels[label_name] = [pin_name, "TRUE", "FALSE", true_color, false_color]
                elif true_text and false_text:
                    parent.hal_bool_labels[label_name] = [pin_name, true_text, false_text, true_color, false_color]
                else:
                    parent.hal_readers[label_name] = pin_name

    if len(hal_ms_labels) > 0:  # setup hal multi state labels
        for item in hal_ms_labels:
            msl_name = item.objectName()
            pin_name = item.property("pin_name")
            if pin_name in dir(parent):
                msg = f"HAL Multi-State Label {label_name}\npin name {pin_name}\nis already used in Flex GUI\nThe HAL pin can not be created."
                print(f"Configuration Error: {msg}")
                continue

            hal_type = item.property("hal_type")
            if hal_type != "HAL_U32":
                item.setEnabled(False)
                msg = f"{hal_type} is not valid for a HAL Multi-State Label\n, only HAL_U32 can be used.\nThe {msl_name} label will be disabled."
                print(f"Configuration Error: {msg}")
                continue

            hal_dir = item.property("hal_dir")
            if hal_dir != "HAL_IN":
                item.setEnabled(False)
                msg = f"{hal_dir} is not a valid\nhal_dir for a HAL Multi-State Lable,\nonly HAL_IN can be used for hal_dir.\nThe {msl_name} Label will be disabled."
                print(f"Configuration Error: {msg}")
                continue

            if msl_name == pin_name:
                item.setEnabled(False)
                msg = f"The object name {msl_name}\ncan not be the same as the\npin name {pin_name}.\nThe HAL object will not be created\nand the label will be disabled."
                print(f"Configuration Error: {msg}")
                continue

            if None not in [pin_name, hal_type, hal_dir]:
                hal_type = getattr(hal, f"{hal_type}")
                hal_dir = getattr(hal, f"{hal_dir}")
                setattr(parent, f"{pin_name}", parent.halcomp.newpin(pin_name, hal_type, hal_dir))
                pin = getattr(parent, f"{pin_name}")
                text = ""
                text_list = []
                i = 0
                while text is not None:
                    text = item.property(f"text_{i}")
                    if text is not None:
                        text_list.append(text)
                    i += 1
                parent.hal_ms_labels[msl_name] = [pin_name, text_list]

    if len(hal_progressbar) > 0:  # setup hal progressbar
        valid_types = ["HAL_S32", "HAL_U32", "HAL_FLOAT"]
        for item in hal_progressbar:
            progressbar_name = item.objectName()
            pin_name = item.property("pin_name")
            if pin_name in dir(parent):
                msg = f"HAL Label {label_name}\npin name {pin_name}\nis already used in Flex GUI\nThe HAL pin can not be created."
                print(f"Configuration Error: {msg}")
                continue

            hal_type = item.property("hal_type")
            if hal_type not in valid_types:
                item.setEnabled(False)
                msg = f"{hal_type} is not valid for a HAL Progressbar\n, only HAL_S32 or HAL_U32\ncan be used. The {progressbar_name} label will be disabled."
                print(f"Configuration Error: {msg}")
                continue

            hal_dir = item.property("hal_dir")
            if hal_dir != "HAL_IN":
                item.setEnabled(False)
                msg = f"{hal_dir} is not a valid\nhal_dir for a HAL Lable,\nonly HAL_IN can be used for hal_dir.\nThe {progressbar_name} Label will be disabled."
                print(f"Configuration Error: {msg}")
                continue

            if progressbar_name == pin_name:
                item.setEnabled(False)
                msg = f"The object name {progressbar_name}\ncan not be the same as the\npin name {pin_name}.\nThe HAL object will not be created\nand the label will be disabled."
                print(f"Configuration Error: {msg}")
                continue

            if None not in [pin_name, hal_type, hal_dir]:
                hal_type = getattr(hal, f"{hal_type}")
                hal_dir = getattr(hal, f"{hal_dir}")
                if hal_type == 2:
                    item.setMinimum(item.minimum() * 100)
                    item.setMaximum(item.maximum() * 100)
                setattr(parent, f"{pin_name}", parent.halcomp.newpin(pin_name, hal_type, hal_dir))
                pin = getattr(parent, f"{pin_name}")
                parent.hal_progressbars[progressbar_name] = pin_name

    if len(hal_buttons) > 0:  # setup hal buttons and checkboxes
        for button in hal_buttons:
            button_name = button.objectName()
            pin_name = button.property("pin_name")
            if pin_name in dir(parent):
                button.setEnabled(False)
                msg = f"HAL Button {button_name}\npin name {pin_name}\nis already used in Flex GUI\nThe HAL pin can not be created.The {button_name} button will be disabled."
                print(f"Configuration Error: {msg}")
                continue

            if button_name == pin_name:
                button.setEnabled(False)
                msg = f"The object name {button_name}\ncan not be the same as the\npin name {pin_name}.\nThe HAL object will not be created\nThe {button_name} button will be disabled."
                print(f"Configuration Error: {msg}")
                continue

            hal_type = button.property("hal_type")
            if hal_type != "HAL_BIT":
                button.setEnabled(False)
                msg = f"{hal_type} is not a valid\nhal_type for a HAL Button,\nonly HAL_BIT can be used for hal_type.\nThe {button_name} button will be disabled."
                print(f"Configuration Error: {msg}")
                continue

            hal_dir = button.property("hal_dir")
            if hal_dir not in {"HAL_OUT", "HAL_IN"}:
                button.setEnabled(False)
                msg = f"{hal_dir} is not a valid\nhal_dir for a HAL Button,\nonly HAL_OUT can be used for hal_dir.\nThe {button_name} button will be disabled."
                print(f"Configuration Error: {msg}")
                continue

            if None not in [pin_name, hal_type, hal_dir]:
                hal_type = getattr(hal, f"{hal_type}")
                hal_dir = getattr(hal, f"{hal_dir}")
                setattr(parent, f"{pin_name}", parent.halcomp.newpin(pin_name, hal_type, hal_dir))
                pin = getattr(parent, f"{pin_name}")

                if button.isCheckable():
                    button.toggled.connect(lambda checked, pin=pin: (pin.set(checked)))
                    # set the hal pin default
                    setattr(parent.halcomp, pin_name, button.isChecked())
                else:
                    button.pressed.connect(lambda pin=pin: (pin.set(True)))
                    button.released.connect(lambda pin=pin: (pin.set(False)))

                parent.state_estop[button_name] = False
                if button.property("state_off") == "disabled":
                    parent.state_estop_reset[button_name] = False
                else:
                    parent.state_estop_reset[button_name] = True

                if button.property("required") == "homed":
                    parent.home_required.append(button_name)
                else:
                    if button_name != "tool_changed_pb":
                        parent.state_on[button_name] = True

    if len(hal_spinboxes) > 0:  # setup hal spinboxes
        valid_types = ["HAL_FLOAT", "HAL_S32", "HAL_U32"]
        for spinbox in hal_spinboxes:
            spinbox_name = spinbox.objectName()
            pin_name = spinbox.property("pin_name")
            if pin_name in dir(parent):
                spinbox.setEnabled(False)
                msg = f"HAL Spinbox {spinbox_name}\npin name {pin_name}\nis already used in Flex GUI\nThe HAL pin can not be created.The {spinbox_name} spinbox will be disabled."
                print(f"Configuration Error: {msg}")
                continue

            if spinbox_name == pin_name:
                spinbox.setEnabled(False)
                msg = f"The object name {spinbox_name}\ncan not be the same as the\npin name {pin_name}.\nThe HAL object will not be created\nThe {spinbox_name} spinbox will be disabled."
                print(f"Configuration Error: {msg}")
                continue

            hal_type = spinbox.property("hal_type")
            if hal_type not in valid_types:
                spinbox.setEnabled(False)
                msg = f"{hal_type} is not valid\nfor a HAL spinbox, only\nHAL_FLOAT or HAL_S32 or HAL_U32\nThe {spinbox_name} spinbox will be disabled."
                print(f"Configuration Error: {msg}")
                continue

            hal_dir = spinbox.property("hal_dir")
            if hal_dir != "HAL_OUT":
                spinbox.setEnabled(False)
                msg = f"{hal_dir} is not a valid\nhal_dir for a HAL Spinbox,\nonly HAL_OUT can be used for hal_dir.\nThe {spinbox_name} spinbox will be disabled."
                print(f"Configuration Error: {msg}")
                continue

            if None not in [pin_name, hal_type, hal_dir]:
                hal_type = getattr(hal, f"{hal_type}")
                hal_dir = getattr(hal, f"{hal_dir}")
                parent.halcomp.newpin(pin_name, hal_type, hal_dir)
                # set the default value of the spin box to the hal pin
                setattr(parent.halcomp, pin_name, spinbox.value())
                spinbox.valueChanged.connect(partial(utilities.update_hal_spinbox, parent))
                parent.state_estop[spinbox_name] = False
                parent.state_estop_reset[spinbox_name] = False
                if parent.probe_controls and spinbox_name.startswith("probe_"):  # don't enable it when power is on
                    parent.probe_controls.append(spinbox_name)
                elif spinbox.property("required") == "homed":
                    parent.home_required.append(spinbox_name)
                else:
                    parent.state_on[spinbox_name] = True

    if len(hal_sliders) > 0:  # setup hal sliders
        valid_types = ["HAL_S32", "HAL_U32", "HAL_FLOAT"]
        for slider in hal_sliders:
            slider_name = slider.objectName()
            pin_name = slider.property("pin_name")
            if pin_name in dir(parent):
                slider.setEnabled(False)
                msg = f"HAL Slider {slider_name}\npin name {pin_name}\nis already used in Flex GUI\nThe HAL pin can not be created."
                f"The {slider_name} slider will be disabled."
                print(f"Configuration Error: {msg}")
                continue

            if slider_name == pin_name:
                slider.setEnabled(False)
                msg = f"The object name {slider_name}\ncan not be the same as the\npin name {pin_name}.\nThe HAL object will not be created\nThe {slider_name} slider will be disabled."
                print(f"Configuration Error: {msg}")
                continue

            hal_type = slider.property("hal_type")
            if hal_type not in valid_types:
                slider.setEnabled(False)
                msg = f"{hal_type} is not valid\nfor a HAL slider, only\nHAL_S32 or HAL_U32 are valid\nThe {slider_name} slider will be disabled."
                print(f"Configuration Error: {msg}")
                continue

            hal_dir = slider.property("hal_dir")
            if hal_dir != "HAL_OUT":
                slider.setEnabled(False)
                msg = f"{hal_dir} is not a valid\nhal_dir for a HAL Slider,\nonly HAL_OUT can be used for hal_dir.\nThe {slider_name} slider will be disabled."
                print(f"Configuration Error: {msg}")
                continue

            if None not in [pin_name, hal_type, hal_dir]:
                hal_type = getattr(hal, f"{hal_type}")
                hal_dir = getattr(hal, f"{hal_dir}")
                parent.halcomp.newpin(pin_name, hal_type, hal_dir)
                # set the default value of the spin box to the hal pin
                setattr(parent.halcomp, pin_name, slider.value())
                if hal_type == 2:
                    slider.setMinimum(slider.minimum() * 100)
                    slider.setMaximum(slider.maximum() * 100)
                slider.valueChanged.connect(partial(utilities.update_hal_slider, parent))
                parent.state_estop[slider_name] = False
                parent.state_estop_reset[slider_name] = False
                if parent.probe_controls and slider_name.startswith("probe_"):  # don't enable it when power is on
                    parent.probe_controls.append(slider_name)
                elif slider.property("required") == "homed":
                    parent.home_required.append(slider_name)
                else:
                    parent.state_on[slider_name] = True
                parent.state_on[slider_name] = True

    if len(hal_leds) > 0:  # setup hal leds
        for led in hal_leds:
            hal_type = getattr(hal, f"{led.property('hal_type')}")
            hal_dir = getattr(hal, f"{led.property('hal_dir')}")
            pin_name = led.property("pin_name")
            setattr(parent, f"{pin_name}", parent.halcomp.newpin(pin_name, hal_type, hal_dir))

    parent.halcomp.ready()
    if "hal_comp_name_lb" in parent.children:
        parent.hal_comp_name_lb.setText(f"{parent.halcomp}")


def setup_tool_change(parent):
    if parent.manual_tool_change:
        if hal.component_exists("hal_manualtoolchange"):
            msg = "The Flex Manual Tool Change\ncan not function with the hal_manualtoolchange\ncomponent. You must find and remove the\nhal_manualtoolchange component!\nSee the Docs for more info."
            print(f"Configuration Error: {msg}")
            parent.manual_tool_change = False
            return

        parent.toolcomp.newpin("number", hal.HAL_S32, hal.HAL_IN)
        parent.toolcomp.newpin("change", hal.HAL_BIT, hal.HAL_IN)
        parent.toolcomp.newpin("changed", hal.HAL_BIT, hal.HAL_OUT)
        parent.toolcomp.ready()
        parent.tool_change = hal.get_value("tool-change.change")

        hal.new_sig("tool-prepare-loopback", hal.HAL_BIT)
        hal.connect("iocontrol.0.tool-prepare", "tool-prepare-loopback")
        hal.connect("iocontrol.0.tool-prepared", "tool-prepare-loopback")

        hal.new_sig("tool-number", hal.HAL_S32)
        hal.connect("iocontrol.0.tool-prep-number", "tool-number")
        hal.connect("tool-change.number", "tool-number")

        hal.new_sig("tool-change", hal.HAL_BIT)
        hal.connect("iocontrol.0.tool-change", "tool-change")
        hal.connect("tool-change.change", "tool-change")


def setup_toolbar(parent):
    if "flex_E_Stop" in parent.children:
        parent.flex_E_Stop.setStyleSheet(parent.selected_style)


def setup_plot(parent):
    if "plot_widget" in parent.children:
        # add the plotter to the container
        from libflexgui import flexplot

        parent.plotter = flexplot.emc_plot(parent)
        layout = QVBoxLayout(parent.plot_widget)
        layout.addWidget(parent.plotter)

        # FIXME move to read_ini.py
        dro_font = parent.inifile.find("DISPLAY", "DRO_FONT_SIZE") or False
        if dro_font:
            msg = "DRO_FONT_SIZE has been moved to the [FLEXGUI]\nsection of the ini file.\nFor now it will still work but soon\nit will be removed so get it changed."
            print(f"INI Configuration ERROR: {msg}")
        else:  # look in the new spot
            dro_font = parent.inifile.find("FLEXGUI", "DRO_FONT_SIZE") or "12"

        parent.plotter._font = f"monospace bold {dro_font}"

        if parent.plot_background_color:
            parent.plotter.background_color = parent.plot_background_color

        # set view in plotter to default view
        parent.plotter.current_view = parent.default_view

        # set view push button for current view selected
        match parent.default_view:
            case "p" if "flex_View_P" in parent.children:
                parent.flex_View_P.setStyleSheet(parent.selected_style)
            case "x" if "flex_View_X" in parent.children:
                parent.flex_View_X.setStyleSheet(parent.selected_style)
            case "y" if "flex_View_Y" in parent.children:
                parent.flex_View_Y.setStyleSheet(parent.selected_style)
            case "y2" if "flex_View_Y2" in parent.children:
                parent.flex_View_Y2.setStyleSheet(parent.selected_style)
            case "z" if "flex_View_Z" in parent.children:
                parent.flex_View_Z.setStyleSheet(parent.selected_style)
            case "z2" if "flex_View_Z2" in parent.children:
                parent.flex_View_Z2.setStyleSheet(parent.selected_style)
            case _:  # default view does not have a pushbutton
                print("default view button not found")

        # key object name, value[0] function, value[1] plot function
        plot_actions = {
            "actionDRO": ["action_toggle_dro", "enable_dro"],
            "actionLimits": ["action_toggle_limits", "show_limits"],
            "actionExtents_Option": ["action_toggle_extents_option", "show_extents_option"],
            "actionLive_Plot": ["action_toggle_live_plot", "show_live_plot"],
            "actionVelocity": ["action_toggle_velocity", "show_velocity"],
            "actionMetric_Units": ["action_toggle_metric_units", "metric_units"],
            "actionProgram": ["action_toggle_program", "show_program"],
            "actionRapids": ["action_toggle_rapids", "show_rapids"],
            "actionTool": ["action_toggle_tool", "show_tool"],
            "actionLathe_Radius": ["action_toggle_lathe_radius", "show_lathe_radius"],
            "actionDTG": ["action_toggle_dtg", "show_dtg"],
            "actionOffsets": ["action_toggle_offsets", "show_offsets"],
            "actionOverlay": ["action_toggle_overlay", "show_overlay"],
        }

        for key, value in plot_actions.items():
            if key in parent.children:
                getattr(parent, f"{key}").triggered.connect(partial(getattr(actions, f"{value[0]}"), parent))
                getattr(parent, key).setCheckable(True)
                if parent.settings.contains(f"PLOT/{key}"):
                    state = True if parent.settings.value(f"PLOT/{key}") == "true" else False
                else:  # add it and set to default
                    state = getattr(parent.plotter, value[1])
                    parent.settings.beginGroup("PLOT")
                    parent.settings.setValue(key, state)
                    parent.settings.endGroup()
                getattr(parent, key).setChecked(state)
                setattr(parent.plotter, value[1], state)

        view_checkboxes = {
            "view_dro_cb": ["action_toggle_dro", "enable_dro"],
            "view_limits_cb": ["action_toggle_limits", "show_limits"],
            "view_extents_option_cb": ["action_toggle_extents_option", "show_extents_option"],
            "view_live_plot_cb": ["action_toggle_live_plot", "show_live_plot"],
            "view_velocity_cb": ["action_toggle_velocity", "show_velocity"],
            "view_metric_units_cb": ["action_toggle_metric_units", "metric_units"],
            "view_program_cb": ["action_toggle_program", "show_program"],
            "view_rapids_cb": ["action_toggle_rapids", "show_rapids"],
            "view_tool_cb": ["action_toggle_tool", "show_tool"],
            "view_lathe_radius_cb": ["action_toggle_lathe_radius", "show_lathe_radius"],
            "view_dtg_cb": ["action_toggle_dtg", "show_dtg"],
            "view_offsets_cb": ["action_toggle_offsets", "show_offsets"],
            "view_overlay_cb": ["action_toggle_overlay", "show_overlay"],
        }

        # if a checkbox is found connect it to the function
        for key, value in view_checkboxes.items():
            if key in parent.children:
                getattr(parent, f"{key}").clicked.connect(partial(getattr(actions, f"{value[0]}"), parent))
                if parent.settings.contains(f"PLOT/{key}"):
                    state = True if parent.settings.value(f"PLOT/{key}") == "true" else False
                else:  # add it and set to default
                    state = getattr(parent.plotter, value[1])
                    parent.settings.beginGroup("PLOT")
                    parent.settings.setValue(key, state)
                    parent.settings.endGroup()
                getattr(parent, key).setChecked(state)
                setattr(parent.plotter, value[1], state)

        view_pushbuttons = {
            "view_dro_pb": ["action_toggle_dro", "enable_dro"],
            "view_limits_pb": ["action_toggle_limits", "show_limits"],
            "view_extents_option_pb": ["action_toggle_extents_option", "show_extents_option"],
            "view_live_plot_pb": ["action_toggle_live_plot", "show_live_plot"],
            "view_velocity_pb": ["action_toggle_velocity", "show_velocity"],
            "view_metric_units_pb": ["action_toggle_metric_units", "metric_units"],
            "view_program_pb": ["action_toggle_program", "show_program"],
            "view_rapids_pb": ["action_toggle_rapids", "show_rapids"],
            "view_tool_pb": ["action_toggle_tool", "show_tool"],
            "view_lathe_radius_pb": ["action_toggle_lathe_radius", "show_lathe_radius"],
            "view_dtg_pb": ["action_toggle_dtg", "show_dtg"],
            "view_offsets_pb": ["action_toggle_offsets", "show_offsets"],
            "view_overlay_pb": ["action_toggle_overlay", "show_overlay"],
        }

        # if a pushbutton is found connect it to the function
        for key, value in view_pushbuttons.items():
            if key in parent.children:
                getattr(parent, f"{key}").clicked.connect(partial(getattr(actions, f"{value[0]}"), parent))
                getattr(parent, f"{key}").setCheckable(True)
                if parent.settings.contains(f"PLOT/{key}"):
                    state = True if parent.settings.value(f"PLOT/{key}") == "true" else False
                else:  # add it and set to default
                    state = getattr(parent.plotter, value[1])
                    parent.settings.beginGroup("PLOT")
                    parent.settings.setValue(key, state)
                    parent.settings.endGroup()
                getattr(parent, key).setChecked(state)
                setattr(parent.plotter, value[1], state)

        parent.plotter.update()

        view_controls = {
            "view_rotate_up_pb": ("rotateView", 0, -5),
            "view_rotate_down_pb": ("rotateView", 0, 5),
            "view_rotate_left_pb": ("rotateView", 5, 0),
            "view_rotate_right_pb": ("rotateView", -5, 0),
            "view_pan_up_pb": ("panView", 0, -5),
            "view_pan_down_pb": ("panView", 0, 5),
            "view_pan_left_pb": ("panView", -5, 0),
            "view_pan_right_pb": ("panView", 5, 0),
            "view_zoom_in_pb": ("zoomin",),
            "view_zoom_out_pb": ("zoomout",),
            "view_clear_pb": ("clear_live_plotter",),
        }

        for key, value in view_controls.items():
            if key in parent.children:
                button = getattr(parent, key)
                if len(value) == 3:
                    method, vertical, horizontal = value
                    button.clicked.connect(lambda _, m=method, v=vertical, h=horizontal: (getattr(parent.plotter, m)(vertical=v, horizontal=h)))
                elif len(value) == 1:
                    method = value[0]
                    button.clicked.connect(lambda _, m=method: (getattr(parent.plotter, m)()))

        views = {"view_p_pb": "p", "view_x_pb": "x", "view_y_pb": "y", "view_y2_pb": "y2", "view_z_pb": "z", "view_z2_pb": "z2"}

        # this connects the view buttons to the plotter
        for key, value in views.items():
            if key in parent.children:
                button = getattr(parent, key)
                button.clicked.connect(lambda _, v=value: (parent.plotter.makeCurrent(), setattr(parent.plotter, "current_view", v), parent.plotter.set_current_view()))

        action_view_controls = {"actionView_Zoom_In": "zoomin", "actionView_Zoom_Out": "zoomout", "actionView_Clear": "clear_live_plotter"}

        for key, value in action_view_controls.items():
            if key in parent.children:
                action = getattr(parent, key)
                action.triggered.connect(lambda _, m=value: (getattr(parent.plotter, m)()))

        # toolbar view actions
        view_actions = {
            "actionView_P": "p",
            "actionView_X": "x",
            "actionView_Y": "y",
            "actionView_Y2": "y2",
            "actionView_Z": "z",
            "actionView_Z2": "z2",
        }

        for key, value in view_actions.items():
            if key in parent.children:
                action = getattr(parent, key)
                action.triggered.connect(
                    lambda _, v=value: (parent.plotter.makeCurrent(), setattr(parent.plotter, "current_view", v), parent.plotter.set_current_view(), utilities.sync_toolbuttons(parent, v))
                )


def setup_fsc(parent):  # mill feed and speed calculator
    if "fsc_container" in parent.children:
        from libflexgui import fsc

        parent.fsc_calc = fsc.fs_calc()
        layout = QVBoxLayout(parent.fsc_container)
        layout.addWidget(parent.fsc_calc)
        if parent.fsc_container.property("input") == "number":
            fsc_items = ["fsc_diameter_le", "fsc_rpm_le", "fsc_flutes_le", "fsc_feed_le", "fsc_chip_load_le"]
            for item in fsc_items:
                getattr(parent.fsc_calc, f"{item}").installEventFilter(parent)
                parent.number_le.append(item)


def setup_dsf(parent):  # drill speed and feed calculator
    if "dsf_container" in parent.children:
        from libflexgui import dsf

        parent.dsf_calc = dsf.dsf_calc()
        layout = QVBoxLayout(parent.dsf_container)
        layout.addWidget(parent.dsf_calc)
        if parent.dsf_container.property("input") == "number":
            dsf_items = ["dfs_diameter_le", "dfs_surface_speed_le"]
            for item in dsf_items:
                getattr(parent.dsf_calc, f"{item}").installEventFilter(parent)
                parent.number_le.append(item)


def setup_tpc(parent):  # three point center calculator
    if "tpc_container" in parent.children:
        from libflexgui import tpc

        parent.tpc_calc = tpc.tpc_calc(parent)
        layout = QVBoxLayout(parent.tpc_container)
        layout.addWidget(parent.tpc_calc)


def setup_import(parent):
    modules = parent.inifile.findall("FLEXGUI", "IMPORT_PYTHON") or False
    if modules:
        for module_name in modules:
            module_path = os.path.join(parent.config_path, f"{module_name}.py")
            if os.path.exists(module_path):
                try:
                    sys.path.append(parent.config_path)
                    module = importlib.import_module(module_name)
                    module.startup(parent)
                except Exception:
                    print(traceback.format_exc())
                    msg = f"The python file\n{module_path}\nhas an error in the module code.\n{traceback.format_exc()}"
                    print(f"Import Failed: {msg}")
            else:
                msg = f"The python file\n{module_path}\nwas not found.\n"
                print(f"Import Failed: {msg}")


def setup_help(parent):
    children = parent.findChildren(QPushButton)
    for child in children:
        if child.property("function") == "help":
            child.clicked.connect(partial(dialogs.help_dialog, parent))


def set_status(parent):  # this is only used if running from a terminal
    parent.status.poll()
    if parent.status.task_state == emc.STATE_ESTOP:
        for key, value in parent.state_estop.items():
            getattr(parent, key).setEnabled(value)
        for key, value in parent.state_estop_names.items():
            getattr(parent, key).setText(value)
