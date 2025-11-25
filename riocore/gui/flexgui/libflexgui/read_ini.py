import os

from PyQt5.QtCore import QSettings
from PyQt5.QtGui import QColor
from libflexgui import dialogs, utilities


def read(parent):
    # ***** [FLEXGUI] Section *****
    # check for theme must be done before using any dialogs
    parent.theme = parent.inifile.find("FLEXGUI", "THEME") or False

    # ***** [EMC] Section *****
    machine_name = parent.inifile.find("EMC", "MACHINE") or False
    if machine_name:
        parent.settings = QSettings("Flex", machine_name)
    else:
        parent.settings = QSettings("Flex", "unknown")

    # ***** [DISPLAY] Section *****
    # get file extensions
    parent.extensions = [".ngc"]  # used by the touch file selector
    extensions = parent.inifile.find("DISPLAY", "EXTENSIONS") or False
    if extensions:  # add any extensions from the ini to ngc
        for ext in extensions.split(","):
            parent.extensions.append(ext.strip())
        extensions = extensions.split(",")
        extensions = " ".join(extensions).strip()
        parent.ext_filter = f"G code Files ({extensions});;All Files (*)"
    else:
        parent.ext_filter = "G code Files (*.ngc *.NGC);;All Files (*)"

    # set the nc code directory to some valid directory
    directory = parent.inifile.find("DISPLAY", "PROGRAM_PREFIX") or False
    ini_dir = False
    if directory:  # expand directory if needed
        ini_dir = True
        if directory.startswith("./"):  # in this directory
            directory = os.path.join(parent.config_path, directory[2:])
        elif directory.startswith("../"):  # up one directory
            directory = os.path.join(os.path.dirname(parent.config_path), directory[3:])
        elif directory.startswith("~"):  # users home directory
            directory = os.path.expanduser(directory)

    if os.path.isdir(directory):
        parent.nc_code_dir = directory
    else:  # try and find a directory
        if os.path.isdir(os.path.expanduser("~/linuxcnc/nc_files")):
            parent.nc_code_dir = os.path.expanduser("~/linuxcnc/nc_files")
        else:
            parent.nc_code_dir = os.path.expanduser("~/")
        if ini_dir:  # a nc code directory was in the ini file but is not valid
            msg = f"The path {directory}\ndoes not exist. Check the\nPROGRAM_PREFIX key in the\n[DISPLAY] section of the\nINI file for a valid path.\n{parent.nc_code_dir} will be used."
            dialogs.warn_msg_ok(parent, msg, "Configuration Error")

    parent.editor = parent.inifile.find("DISPLAY", "EDITOR") or False
    parent.tool_editor = parent.inifile.find("DISPLAY", "TOOL_EDITOR") or False
    if parent.inifile.find("DISPLAY", "LATHE") is not None:
        parent.default_view = "y"
    elif parent.inifile.find("DISPLAY", "VIEW") is not None:
        parent.default_view = parent.inifile.find("DISPLAY", "VIEW")
    else:
        parent.default_view = "p"

    # get spindle increment
    increment = parent.inifile.find("DISPLAY", "SPINDLE_INCREMENT") or False
    if not increment:
        increment = parent.inifile.find("SPINDLE_0", "INCREMENT") or False
    parent.increment = int(increment) if increment else 10

    # ***** [EMCIO] Section *****
    parent.tool_table = parent.inifile.find("EMCIO", "TOOL_TABLE") or False

    # ***** [RS274NGC] Section *****
    parent.var_file = parent.inifile.find("RS274NGC", "PARAMETER_FILE") or False

    # ***** [HAL] Section *****
    parent.postgui_halfiles = parent.inifile.findall("HAL", "POSTGUI_HALFILE") or False

    # ***** [SPINDLE_0] Section *****
    parent.min_rpm = parent.inifile.find("SPINDLE_0", "MIN_FORWARD_VELOCITY") or False
    parent.max_rpm = parent.inifile.find("SPINDLE_0", "MAX_FORWARD_VELOCITY") or False

    # ***** Test for old entries *****
    if parent.inifile.find("DISPLAY", "RESOURCES"):
        msg = "The key RESOURCES has been moved from the [DISPLAY] section\nThe key RESOURCES needs to be in the [FLEXGUI] section\nCheck the INI section of the Documents for correct INI entries."
        dialogs.warn_msg_ok(parent, msg, "Configuration Error")

    if parent.inifile.find("DISPLAY", "SIZE"):
        msg = "The key SIZE has been moved from the [DISPLAY] section\nThe key SIZE needs to be in the [FLEXGUI] section\nCheck the INI section of the Documents for correct INI entries."
        dialogs.warn_msg_ok(parent, msg, "Configuration Error")

    if parent.inifile.find("FLEX_COLORS", "ESTOP_OPEN"):
        msg = "The [FLEX_COLORS] section has been changed to [FLEXGUI]\nThe key ESTOP_OPEN is now ESTOP_OPEN_COLOR\nCheck the INI section of the Documents for correct INI entries."
        dialogs.warn_msg_ok(parent, msg, "Configuration Error")

    if parent.inifile.find("FLEX_COLORS", "ESTOP_CLOSED"):
        msg = "The [FLEX_COLORS] section has been changed to [FLEXGUI]\nThe key ESTOP_CLOSED is now ESTOP_CLOSED_COLOR\nCheck the INI section of the Documents for correct INI entries."
        dialogs.warn_msg_ok(parent, msg, "Configuration Error")

    if parent.inifile.find("FLEX_COLORS", "POWER_OFF"):
        msg = "The [FLEX_COLORS] section has been changed to [FLEXGUI]\nThe key POWER_OFF is now POWER_OFF_COLOR\nCheck the INI section of the Documents for correct INI entries."
        dialogs.warn_msg_ok(parent, msg, "Configuration Error")

    if parent.inifile.find("FLEX_COLORS", "POWER_ON"):
        msg = "The [FLEX_COLORS] section has been changed to [FLEXGUI]\nThe key POWER_ON is now POWER_ON_COLOR\nCheck the INI section of the Documents for correct INI entries."
        dialogs.warn_msg_ok(parent, msg, "Configuration Error")

    if parent.inifile.find("FLEX", "PLOT_BACKGROUND_COLOR"):
        msg = "The [FLEX] section has been changed to [FLEXGUI]\nThe key PLOT_BACKGROUND_COLOR needs to be in the [FLEXGUI] section\nCheck the INI section of the Documents for correct INI entries."
        dialogs.warn_msg_ok(parent, msg, "Configuration Error")

    if parent.inifile.find("FLEX", "TOUCH_FILE_WIDTH"):
        msg = "The [FLEX] section has been changed to [FLEXGUI]\nThe key TOUCH_FILE_WIDTH needs to be in the [FLEXGUI] section\nCheck the INI section of the Documents for correct INI entries."
        dialogs.warn_msg_ok(parent, msg, "Configuration Error")

    if parent.inifile.find("FLEX", "MANUAL_TOOL_CHANGE"):
        msg = "The [FLEX] section has been changed to [FLEXGUI]\nThe key MANUAL_TOOL_CHANGE needs to be in the [FLEXGUI] section\nCheck the INI section of the Documents for correct INI entries."
        dialogs.warn_msg_ok(parent, msg, "Configuration Error")

    if parent.inifile.findall("FLEX", "IMPORT"):
        msg = "The [FLEX] section has been changed to [FLEXGUI]\nThe key IMPORT has been changed to IMPORT_PYTHON\nCheck Python section of the Documents for correct INI entries."
        dialogs.warn_msg_ok(parent, msg, "Configuration Error")

    if parent.inifile.find("DISPLAY", "THEME"):
        msg = "THEME has been moved to the [FLEXGUI]\nsection of the ini file.\nCheck the INI section of the Documents for correct INI entries."
        dialogs.warn_msg_ok(parent, msg, "Configuration Error")

    if parent.inifile.find("DISPLAY", "QSS"):
        msg = "QSS has been moved to the [FLEXGUI]\nsection of the ini file.\nCheck the INI section of the Documents for correct INI entries."
        dialogs.warn_msg_ok(parent, msg, "Configuration Error")

    # check for a RESOURCES
    parent.resources_file = parent.inifile.find("FLEXGUI", "RESOURCES") or False

    # check for QSS
    parent.qss_file = parent.inifile.find("FLEXGUI", "QSS") or False

    # test for both THEME and QSS
    if parent.theme and parent.qss_file:
        msg = f"The THEME {parent.theme} and QSS {parent.qss_file}\nwere both found in the ini file.\nthe QSS {parent.qss_file} will not be used.\nOnly one can be specified in the ini."
        dialogs.warn_msg_ok(parent, msg, "INI Configuration ERROR!")
        parent.qss_file = False

    # check for LED defaults in the ini file
    parent.led_diameter = parent.inifile.find("FLEXGUI", "LED_DIAMETER")
    if parent.led_diameter is None:
        parent.led_diameter = 15
    else:
        parent.led_diameter = int(parent.led_diameter)

    parent.led_right_offset = parent.inifile.find("FLEXGUI", "LED_RIGHT_OFFSET")
    if parent.led_right_offset is None:
        parent.led_right_offset = 5
    else:
        parent.led_right_offset = int(parent.led_right_offset)

    parent.led_top_offset = parent.inifile.find("FLEXGUI", "LED_TOP_OFFSET")
    if parent.led_top_offset is None:
        parent.led_top_offset = 5
    else:
        parent.led_top_offset = int(parent.led_top_offset)

    parent.led_on_color = parent.inifile.find("FLEXGUI", "LED_ON_COLOR") or False
    if parent.led_on_color:  # convert string to QColor
        parent.led_on_color = utilities.string_to_qcolor(parent, parent.led_on_color, "LED_ON_COLOR")
    if not parent.led_on_color:  # use default led on color
        parent.led_on_color = QColor(0, 255, 0, 255)

    parent.led_off_color = parent.inifile.find("FLEXGUI", "LED_OFF_COLOR") or False
    if parent.led_off_color:  # convert string to QColor
        parent.led_off_color = utilities.string_to_qcolor(parent, parent.led_off_color, "LED_OFF_COLOR")
    if not parent.led_off_color:  # use default led on color
        parent.led_off_color = QColor(125, 0, 0, 255)

    parent.estop_open_color = parent.inifile.find("FLEXGUI", "ESTOP_OPEN_COLOR") or False
    if parent.estop_open_color:  # get a valid color string
        color = utilities.string_to_rgba(parent, parent.estop_open_color, "ESTOP_OPEN_COLOR")
        if color:
            parent.estop_open_color = f"background-color: {color};"

    parent.estop_closed_color = parent.inifile.find("FLEXGUI", "ESTOP_CLOSED_COLOR") or False
    if parent.estop_closed_color:  # get a valid color string
        color = utilities.string_to_rgba(parent, parent.estop_closed_color, "ESTOP_CLOSED_COLOR")
        if color:
            parent.estop_closed_color = f"background-color: {color};"

    parent.power_off_color = parent.inifile.find("FLEXGUI", "POWER_OFF_COLOR") or False
    if parent.power_off_color:  # get a valid color string
        color = utilities.string_to_rgba(parent, parent.power_off_color, "POWER_OFF_COLOR")
        if color:
            parent.power_off_color = f"background-color: {color};"

    parent.power_on_color = parent.inifile.find("FLEXGUI", "POWER_ON_COLOR") or False
    if parent.power_on_color:  # get a valid color string
        color = utilities.string_to_rgba(parent, parent.power_on_color, "POWER_ON_COLOR")
        if color:
            parent.power_on_color = f"background-color: {color};"

    parent.probe_enable_on_color = parent.inifile.find("FLEXGUI", "PROBE_ENABLE_ON_COLOR") or False
    if parent.probe_enable_on_color:  # get a valid color string
        color = utilities.string_to_rgba(parent, parent.probe_enable_on_color, "PROBE_ENABLE_ON_COLOR")
        if color:
            parent.probe_enable_on_color = f"background-color: {color};"

    parent.probe_enable_off_color = parent.inifile.find("FLEXGUI", "PROBE_ENABLE_OFF_COLOR") or False
    if parent.probe_enable_off_color:  # get a valid color string
        color = utilities.string_to_rgba(parent, parent.probe_enable_off_color, "PROBE_ENABLE_OFF_COLOR")
        if color:
            parent.probe_enable_off_color = f"background-color: {color};"

    parent.plot_background_color = parent.inifile.find("FLEXGUI", "PLOT_BACKGROUND_COLOR") or False
    if parent.plot_background_color:
        parent.plot_background_color = tuple(map(float, parent.plot_background_color.split(",")))

    parent.manual_tool_change = parent.inifile.find("FLEXGUI", "MANUAL_TOOL_CHANGE") or False

    parent.touch_file_width = parent.inifile.find("FLEXGUI", "TOUCH_FILE_WIDTH") or False
    if parent.touch_file_width in ["True", "true", "1"]:
        parent.touch_file_width = True
    else:
        parent.touch_file_width = False

    parent.enable_kb_jogging = parent.inifile.find("FLEXGUI", "KEYBOARD_JOG") or False

    # ***** [TRAJ] Section *****
    units = parent.inifile.find("TRAJ", "LINEAR_UNITS") or False  # mm or inch
    if units.lower() == "inch":
        parent.units = "in"
        parent.default_precision = 4
    elif units.lower() == "mm":
        parent.units = "mm"
        parent.default_precision = 3
    else:
        parent.default_precision = 4

    """ MAX_LINEAR_VELOCITY = 5.0 - The maximum velocity for any axis or coordinated
	move, in machine units per second. The value shown equals 300 units per minute. """
    parent.max_linear_vel = parent.inifile.find("TRAJ", "MAX_LINEAR_VELOCITY") or False
