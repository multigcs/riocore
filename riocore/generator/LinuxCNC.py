import copy
import glob
import importlib
import os
import shutil
import stat

from riocore import halpins
from riocore.generator.hal import hal_generator
from riocore.generator.component import component
from riocore.generator.pyvcp import pyvcp
from riocore.generator.qtvcp import qtvcp
from riocore.generator.qtpyvcp import qtpyvcp
from riocore.generator.gladevcp import gladevcp

riocore_path = os.path.dirname(os.path.dirname(__file__))


class LinuxCNC:
    AXIS_NAMES = ["X", "Y", "Z", "A", "C", "B", "U", "V", "W"]
    AXIS_DEFAULTS = {
        "MAX_VELOCITY": 40.0,
        "MAX_ACCELERATION": 500.0,
        "MIN_LIMIT": -500,
        "MAX_LIMIT": 1500,
        "MIN_FERROR": 0.01,
        "FERROR": 2.0,
        "BACKLASH": 0.0,
    }
    PID_DEFAULTS = {
        "P": 250.0,
        "I": 0.0,
        "D": 0.0,
        "BIAS": 0.0,
        "FF0": 0.0,
        "FF1": 0.0,
        "FF2": 0.0,
        "DEADBAND": 0.01,
        "MAXOUTPUT": 300,
    }
    JOINT_DEFAULTS = {
        "TYPE": "LINEAR",
        "FERROR": 2.0,
        "MIN_LIMIT": -500.0,
        "MAX_LIMIT": 1500.0,
        "MAX_VELOCITY": 40.0,
        "MAX_ACCELERATION": 500.0,
        "STEPGEN_MAXACCEL": 2000.0,
        "SCALE_OUT": 320.0,
        "SCALE_IN": 320.0,
        "HOME_SEARCH_VEL": -30.0,
        "HOME_LATCH_VEL": 5.0,
        "HOME_FINAL_VEL": 100.0,
        "HOME_IGNORE_LIMITS": "YES",
        "HOME_USE_INDEX": "NO",
        "HOME_OFFSET": 1.0,
        "HOME": 0.0,
        "HOME_SEQUENCE": 0,
    }
    INI_DEFAULTS = {
        "EMC": {
            "MACHINE": "Rio",
            "DEBUG": 0,
            "VERSION": 1.1,
        },
        "DISPLAY": {
            "DISPLAY": "axis",
            "TITLE": "LinuxCNC - RIO",
            "ICON": None,
            "EDITOR": "gedit",
            "POSITION_OFFSET": "RELATIVE",
            "POSITION_FEEDBACK": "ACTUAL",
            "PREFERENCE_FILE_PATH": None,
            "ARCDIVISION": 64,
            "GRIDS": "10mm 20mm 50mm 100mm",
            "INTRO_GRAPHIC": "linuxcnc.gif",
            "INTRO_TIME": 2,
            "PROGRAM_PREFIX": "~/linuxcnc/nc_files",
            "ANGULAR_INCREMENTS": "1, 5, 10, 30, 45, 90, 180, 360",
            "INCREMENTS": "50mm 10mm 5mm 1mm .5mm .1mm .05mm .01mm",
            "SPINDLES": 1,
            "MAX_FEED_OVERRIDE": 5.0,
            "MIN_SPINDLE_OVERRIDE": 0.5,
            "MAX_SPINDLE_OVERRIDE": 1.2,
            "MIN_SPINDLE_SPEED": 120,
            "DEFAULT_SPINDLE_SPEED": 1250,
            "MAX_SPINDLE_SPEED": 3600,
            "MIN_SPINDLE_0_OVERRIDE": 0.5,
            "MAX_SPINDLE_0_OVERRIDE": 1.2,
            "MIN_SPINDLE_0_SPEED": 0,
            "DEFAULT_SPINDLE_0_SPEED": 200,
            "SPINDLE_INCREMENT": 10,
            "MAX_SPINDLE_0_SPEED": 300,
            "MAX_SPINDLE_POWER": 300,
            "MIN_LINEAR_VELOCITY": 0.0,
            "DEFAULT_LINEAR_VELOCITY": 40.0,
            "MAX_LINEAR_VELOCITY": 45.0,
            "MIN_ANGULAR_VELOCITY": 0.0,
            "DEFAULT_ANGULAR_VELOCITY": 2.5,
            "MAX_ANGULAR_VELOCITY": 5.0,
        },
        "KINS": {
            "JOINTS": None,
            "KINEMATICS": None,
        },
        "FILTER": {
            "PROGRAM_EXTENSION|1": ".ngc,.nc,.tap G-Code File (*.ngc,*.nc,*.tap)",
            "PROGRAM_EXTENSION|2": ".py Python Script",
            "py": "python",
        },
        "TASK": {
            "TASK": "milltask",
            "CYCLE_TIME": 0.010,
        },
        "RS274NGC": {
            "PARAMETER_FILE": "linuxcnc.var",
            "SUBROUTINE_PATH": "./subroutines/",
            "USER_M_PATH": "./mcodes/",
        },
        "EMCMOT": {
            "EMCMOT": "motmod",
            "COMM_TIMEOUT": 1.0,
            "COMM_WAIT": 0.010,
            "BASE_PERIOD": 0,
            "SERVO_PERIOD": 1000000,
            "NUM_DIO": None,
            "NUM_AIO": None,
        },
        "HAL": {
            "HALFILE|base": "rio.hal",
            "HALFILE|custom": "pregui_call_list.hal",
            "TWOPASS": "ON",
            "POSTGUI_HALFILE": "postgui_call_list.hal",
            "HALUI": "halui",
        },
        "HALUI": {},
        "TRAJ": {
            "COORDINATES": None,
            "LINEAR_UNITS": "mm",
            "ANGULAR_UNITS": "degree",
            "CYCLE_TIME": 0.010,
            "DEFAULT_LINEAR_VELOCITY": 40.00,
            "MAX_LINEAR_VELOCITY": 45.00,
            "DEFAULT_ANGULAR_VELOCITY": 60.0,
            "MAX_ANGULAR_VELOCITY": 100.0,
            "NO_FORCE_HOMING": 1,
        },
        "EMCIO": {
            "EMCIO": "io",
            "CYCLE_TIME": 0.100,
            "TOOL_TABLE": "tool.tbl",
        },
    }

    def __init__(self, project):
        self.postgui_call_rm = []
        self.postgui_call_list = []
        self.pregui_call_list = []
        self.feedbacks = []
        self.axisout = []
        self.networks = {}
        self.setps = {}
        self.halextras = []
        self.project = project
        self.base_path = os.path.join(self.project.config["output_path"], "LinuxCNC")
        self.component_path = f"{self.base_path}"
        self.configuration_path = f"{self.base_path}"
        self.create_axis_config()
        self.addons = {}
        for addon_path in glob.glob(os.path.join(riocore_path, "generator", "addons", "*", "linuxcnc.py")):
            addon_name = addon_path.split(os.sep)[-2]
            self.addons[addon_name] = importlib.import_module(".linuxcnc", f"riocore.generator.addons.{addon_name}")

    def startscript(self):
        jdata = self.project.config["jdata"]
        startup = jdata.get("startup")
        output = ["#!/bin/sh"]
        output.append("")
        output.append("set -e")
        output.append("set -x")
        output.append("")
        output.append('DIRNAME=`dirname "$0"`')
        output.append("")

        if self.gui_type == "qtvcp":
            output.append("sudo mkdir -p /usr/share/qtvcp/panels/rio-gui/")
            output.append("sudo mkdir -p /usr/share/qtvcp/panels/rio-gui/")
            output.append('sudo cp -a "$DIRNAME/rio-gui_handler.py" /usr/share/qtvcp/panels/rio-gui/')
            output.append('sudo cp -a "$DIRNAME/rio-gui.ui" /usr/share/qtvcp/panels/rio-gui/')

        if startup:
            output.append(startup)
            output.append("")
        output.append('linuxcnc "$DIRNAME/rio.ini" $@')
        output.append("")
        os.makedirs(self.component_path, exist_ok=True)
        target = os.path.join(self.component_path, "start.sh")
        open(target, "w").write("\n".join(output))
        os.chmod(target, stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR | stat.S_IRGRP | stat.S_IXGRP | stat.S_IROTH | stat.S_IXOTH)

    def generator(self):
        jdata = self.project.config["jdata"]
        linuxcnc_config = jdata.get("linuxcnc", {})
        gui = linuxcnc_config.get("gui", "axis")
        vcp_mode = linuxcnc_config.get("vcp_mode", "ALL")
        vcp_type = linuxcnc_config.get("vcp_type", "auto")
        for network, net in linuxcnc_config.get("halsignals", {}).items():
            self.networks[network] = net

        self.gui_gen = None
        self.gui_type = ""
        self.gui_prefix = ""
        if vcp_mode != "NONE":
            if gui == "axis":
                if vcp_type == "gladevcp":
                    self.gui_gen = gladevcp()
                    self.gui_type = "gladevcp"
                    self.gui_prefix = "gladevcp"
                else:
                    self.gui_gen = pyvcp()
                    self.gui_type = "pyvcp"
                    self.gui_prefix = "pyvcp"
            elif gui == "gmoccapy":
                if vcp_type == "pyvcp":
                    self.gui_gen = pyvcp()
                    self.gui_type = "pyvcp"
                    self.gui_prefix = "pyvcp"
                else:
                    self.gui_gen = gladevcp()
                    self.gui_type = "gladevcp"
                    self.gui_prefix = "rio-gui"
            elif gui in {"qtdragon", "qtdragon_hd"}:
                self.gui_gen = qtvcp()
                self.gui_type = "qtvcp"
                self.gui_prefix = "qtdragon.rio-gui"
            elif gui in {"probe_basic", "probe_basic_lathe"}:
                self.gui_gen = qtpyvcp()
                self.gui_type = "qtpyvcp"
                self.gui_prefix = "qtpyvcp.rio"

        self.startscript()
        component(self.project)
        self.hal()
        self.riof()
        self.gui()
        for addon_name, addon in self.addons.items():
            if hasattr(addon, "generator"):
                addon.generator(self)
        self.misc()
        self.ini()
        os.makedirs(self.configuration_path, exist_ok=True)

        output_hal = []
        output_postgui = []

        (network_hal, network_postgui) = self.halg.net_write()
        output_hal += network_hal
        output_postgui += network_postgui
        output_postgui += [""]
        output_hal += self.halextras

        output_hal.append("")
        output_hal += self.axisout
        open(os.path.join(self.configuration_path, "rio.hal"), "w").write("\n".join(output_hal))
        open(os.path.join(self.configuration_path, "custom_postgui.hal"), "w").write("\n".join(output_postgui))

        if gui == "gmoccapy" and self.gui_type == "gladevcp":
            print("## INFO: custom_postgui.hal will be load by gladevcp")
            self.postgui_call_rm.append("custom_postgui.hal")
        else:
            self.postgui_call_list.append("custom_postgui.hal")

        list_data = []
        if os.path.isfile(os.path.join(self.configuration_path, "postgui_call_list.hal")):
            # read existing file to keep custom entry's
            cl_data = open(os.path.join(self.configuration_path, "postgui_call_list.hal"), "r").read()
            for line in cl_data.split("\n"):
                if line.startswith("source "):
                    source = line.split()[1]
                    if source in self.postgui_call_rm:
                        continue
                    elif source in self.postgui_call_list:
                        self.postgui_call_list.remove(source)
                list_data.append(line.strip())

        for halfile in self.postgui_call_list:
            list_data.append(f"source {halfile}")
        open(os.path.join(self.configuration_path, "postgui_call_list.hal"), "w").write("\n".join(list_data))

        extra_data = []
        if os.path.isfile(os.path.join(self.configuration_path, "pregui_call_list.hal")):
            # read existing file to keep custom entry's
            cl_data = open(os.path.join(self.configuration_path, "pregui_call_list.hal"), "r").read()
            for line in cl_data.split("\n"):
                if line.startswith("source "):
                    source = " ".join(line.split()[1:])
                    if source in self.pregui_call_list:
                        continue
                extra_data.append(line.strip())
        cl_output = []
        for halfile in self.pregui_call_list:
            cl_output.append(f"source {halfile}")
        for line in extra_data:
            cl_output.append(line)
        open(os.path.join(self.configuration_path, "pregui_call_list.hal"), "w").write("\n".join(cl_output))

        print(f"writing linuxcnc files to: {self.base_path}")

    def ini_mdi_command(self, command, title=None):
        jdata = self.project.config["jdata"]
        ini = self.ini_defaults(jdata, num_joints=5, axis_dict=self.axis_dict, gui_type=self.gui_type)
        mdi_index = None
        mdi_n = 0
        for key, value in ini["HALUI"].items():
            if key.startswith("MDI_COMMAND|"):
                if value == command:
                    mdi_index = mdi_n
                    break
                mdi_n += 1
        if mdi_index is None:
            mdi_index = mdi_n
            if title:
                ini["HALUI"][f"MDI_COMMAND|{title}"] = command
            else:
                ini["HALUI"][f"MDI_COMMAND|{mdi_index:02d}"] = command
        return f"halui.mdi-command-{mdi_index:02d}"

    @classmethod
    def ini_defaults(cls, jdata, num_joints=5, axis_dict={}, dios=16, aios=16, gui_type="pyvcp"):
        linuxcnc_config = jdata.get("linuxcnc", {})
        ini_setup = cls.INI_DEFAULTS.copy()
        gui = linuxcnc_config.get("gui", "axis")
        machinetype = linuxcnc_config.get("machinetype")
        embed_vismach = linuxcnc_config.get("embed_vismach")

        netlist = []
        for plugin in jdata["plugins"]:
            for signal in plugin.get("signals", {}).values():
                if net := signal.get("net"):
                    netlist.append(net)

        if machinetype:
            ini_setup["EMC"]["MACHINE"] = f"Rio - {machinetype}"

        if machinetype == "lathe":
            ini_setup["DISPLAY"]["LATHE"] = 1

        coordinates = []
        for axis_name, axis_config in axis_dict.items():
            joints = axis_config["joints"]
            for joint, joint_setup in joints.items():
                coordinates.append(axis_name)

        for section, section_options in linuxcnc_config.get("ini", {}).items():
            if section not in ini_setup:
                ini_setup[section] = {}
            for key, value in section_options.items():
                ini_setup[section][key] = value

        kinematics = "trivkins"
        kinematics_options = f" coordinates={''.join(coordinates)}"
        if machinetype == "ldelta":
            kinematics = "lineardeltakins"
            kinematics_options = ""
        elif machinetype == "rdelta":
            kinematics = "rotarydeltakins"
            kinematics_options = ""
        elif machinetype in {"scara"}:
            kinematics = "scarakins"
            kinematics_options = " coordinates=xyzcab"
        elif machinetype in {"puma"}:
            kinematics = "pumakins"
            kinematics_options = ""
        elif machinetype in {"melfa"}:
            kinematics = "genserkins"
            kinematics_options = ""
            ini_setup["RS274NGC"]["RS274NGC_STARTUP_CODE"] = "G10 L2 P7 X0 Y0 Z0 A-180 B0 C0 G59.1"
            ini_setup["RS274NGC"]["HAL_PIN_VARS"] = "1"
            ini_setup["RS274NGC"]["REMAP|M428"] = "M428 modalgroup=10 ngc=428remap"
            ini_setup["RS274NGC"]["REMAP|M429"] = "M429 modalgroup=10 ngc=429remap"
            ini_setup["RS274NGC"]["REMAP|M430"] = "M430 modalgroup=10 ngc=430remap"
            ini_setup["HALUI"]["MDI_COMMAND||Coord|World"] = "M428"
            ini_setup["HALUI"]["MDI_COMMAND||Coord|Joint"] = "M429"
            ini_setup["HALUI"]["MDI_COMMAND||Coord|Gensertool"] = "M430"

        if embed_vismach:
            ini_setup["DISPLAY"]["EMBED_TAB_NAME|VISMACH"] = "Vismach"
            ini_setup["DISPLAY"]["EMBED_TAB_COMMAND|VISMACH"] = f"halcmd loadusr -Wn qtvcp_embed qtvcp -d -c qtvcp_embed -x {{XID}} vismach_{embed_vismach}"

        ini_setup["KINS"]["JOINTS"] = num_joints
        ini_setup["KINS"]["KINEMATICS"] = f"{kinematics}{kinematics_options}"
        ini_setup["TRAJ"]["COORDINATES"] = "".join(coordinates)
        ini_setup["EMCMOT"]["NUM_DIO"] = dios
        ini_setup["EMCMOT"]["NUM_AIO"] = aios

        for axis_name, axis_config in axis_dict.items():
            ini_setup["HALUI"][f"MDI_COMMAND|Zero-{axis_name}"] = f"G92 {axis_name}0"
            if "motion.probe-input" in netlist:
                if machinetype == "lathe":
                    if axis_name == "X":
                        ini_setup["HALUI"]["MDI_COMMAND|Touch-X"] = "o<x_touch> call"
                    elif axis_name == "Z":
                        ini_setup["HALUI"]["MDI_COMMAND|Touch-Z"] = "o<z_touch> call"
                else:
                    if axis_name == "Z":
                        ini_setup["HALUI"]["MDI_COMMAND|Touch-Z"] = "o<z_touch> call"

        if gui == "axis":
            if gui_type == "pyvcp":
                vcp_pos = linuxcnc_config.get("vcp_pos", "RIGHT")
                if vcp_pos == "TAB":
                    ini_setup["DISPLAY"]["EMBED_TAB_NAME|PYVCP"] = "pyvcp"
                    ini_setup["DISPLAY"]["EMBED_TAB_COMMAND|PYVCP"] = "pyvcp rio-gui.xml"
                else:
                    ini_setup["DISPLAY"]["PYVCP_POSITION"] = vcp_pos
                    ini_setup["DISPLAY"]["PYVCP"] = "rio-gui.xml"
            elif gui_type == "gladevcp":
                ini_setup["DISPLAY"]["GLADEVCP"] = "-u rio-gui.py rio-gui.ui"

        elif gui == "gmoccapy":
            ini_setup["DISPLAY"]["DISPLAY"] = gui
            ini_setup["DISPLAY"]["CYCLE_TIME"] = "150"
            if gui_type == "pyvcp":
                ini_setup["DISPLAY"]["EMBED_TAB_NAME|PYVCP"] = "RIO"
                ini_setup["DISPLAY"]["EMBED_TAB_LOCATION|PYVCP"] = "ntb_user_tabs"
                ini_setup["DISPLAY"]["EMBED_TAB_COMMAND|PYVCP"] = "pyvcp rio-gui.xml"
            elif gui_type == "gladevcp":
                ini_setup["DISPLAY"]["EMBED_TAB_NAME|PYVCP"] = "RIO"
                ini_setup["DISPLAY"]["EMBED_TAB_LOCATION|PYVCP"] = "box_right"
                ini_setup["DISPLAY"]["EMBED_TAB_COMMAND|PYVCP"] = "gladevcp -x {XID} -H custom_postgui.hal rio-gui.ui"

        elif gui in {"probe_basic", "probe_basic_lathe"}:
            ini_setup["DISPLAY"]["DISPLAY"] = gui

            pb_setup = {
                "DISPLAY": {
                    "DISPLAY": gui,
                    "CONFIG_FILE": "custom_config.yml",
                    "INTRO_GRAPHIC": "pbsplash.png",
                    "INTRO_TIME": "2",
                    "USER_TABS_PATH": "user_tabs/",
                    "USER_BUTTONS_PATH": "user_buttons/",
                },
            }

            for section, sdata in pb_setup.items():
                if section not in ini_setup:
                    ini_setup[section] = {}
                for key, value in sdata.items():
                    ini_setup[section][key] = value

        elif gui in {"qtdragon", "qtdragon_hd"}:
            qtdragon_setup = {
                "DISPLAY": {
                    "DISPLAY": f"qtvcp {gui}",
                    "PREFERENCE_FILE_PATH": "WORKINGFOLDER/qtdragon.pref",
                    "MDI_HISTORY_FILE": "mdi_history.dat",
                    "MACHINE_LOG_PATH": "machine_log.dat",
                    "LOG_FILE": "qtdragon.log",
                    "ICON": "silver_dragon.png",
                    "INTRO_GRAPHIC": "silver_dragon.png",
                    "INTRO_TIME": "1",
                    "CYCLE_TIME": "100",
                    "GRAPHICS_CYCLE_TIME": "100",
                    "HALPIN_CYCLE": "100",
                },
                "PROBE": {
                    "USE_PROBE": "NO",
                },
            }
            if gui_type == "qtvcp":
                qtdragon_setup["DISPLAY"]["EMBED_TAB_NAME|RIO"] = "RIO"
                qtdragon_setup["DISPLAY"]["EMBED_TAB_COMMAND|RIO"] = "qtvcp rio-gui"
                qtdragon_setup["DISPLAY"]["EMBED_TAB_LOCATION|RIO"] = "tabWidget_utilities"

            for section, sdata in qtdragon_setup.items():
                if section not in ini_setup:
                    ini_setup[section] = {}
                for key, value in sdata.items():
                    ini_setup[section][key] = value
        elif gui == "qtplasmac":
            ini_setup["EMC"]["MACHINE"] = "qtplasmac-metric"
            ini_setup["DISPLAY"]["DISPLAY"] = "qtvcp qtplasmac"
            ini_setup["RS274NGC"]["RS274NGC_STARTUP_CODE"] = "G21 G40 G49 G80 G90 G92.1 G94 G97 M52P1"
        else:
            ini_setup["DISPLAY"]["DISPLAY"] = gui
        return ini_setup

    def ini(self):
        jdata = self.project.config["jdata"]
        json_path = self.project.config["json_path"]
        linuxcnc_config = jdata.get("linuxcnc", {})
        gui = linuxcnc_config.get("gui", "axis")
        dios = 16
        aios = 16
        for net_name, net_nodes in self.networks.items():
            for net in net_nodes.get("in", []):
                if net.startswith("motion.digital-out-"):
                    dios = max(dios, int(net.split("-")[-1]) + 1)
                if net.startswith("motion.analog-out-"):
                    aios = max(dios, int(net.split("-")[-1]) + 1)
            for net in net_nodes.get("out", []):
                if net.startswith("motion.digital-in-"):
                    dios = max(dios, int(net.split("-")[-1]) + 1)
                if net.startswith("motion.analog-in-"):
                    aios = max(dios, int(net.split("-")[-1]) + 1)
        if dios > 64:
            print("ERROR: you can only configure up to 64 motion.digital-in-NN/motion.digital-out-NN")
        if aios > 64:
            print("ERROR: you can only configure up to 64 motion.analog-in-NN/motion.analog-out-NN")

        ini_setup = self.ini_defaults(self.project.config["jdata"], num_joints=self.num_joints, axis_dict=self.axis_dict, dios=dios, aios=aios, gui_type=self.gui_type)

        for section, section_options in linuxcnc_config.get("ini", {}).items():
            if section not in ini_setup:
                ini_setup[section] = {}
            for key, value in section_options.items():
                ini_setup[section][key] = value

        for addon_name, addon in self.addons.items():
            if hasattr(addon, "ini"):
                addon.ini(self, ini_setup)

        output = []
        for section, setup in ini_setup.items():
            output.append(f"[{section}]")
            for key, value in setup.items():
                if isinstance(value, list):
                    for entry in value:
                        output.append(f"{key} = {entry}")
                elif value is not None:
                    if "|" in key:
                        key = key.split("|")[0]
                    if key.endswith("_VELOCITY") and "ANGULAR" not in key:
                        output.append(f"# {value} * 60.0 = {float(value) * 60.0:0.1f} units/min")
                    output.append(f"{key} = {value}")
            output.append("")

        for axis_name, axis_config in self.axis_dict.items():
            joints = axis_config["joints"]
            output.append(f"[AXIS_{axis_name}]")
            axis_setup = copy.deepcopy(self.AXIS_DEFAULTS)
            axis_max_velocity = 10000.0
            axis_max_acceleration = 10000.0
            axis_min_limit = 100000.0
            axis_max_limit = -100000.0
            axis_backlash = 0.0
            axis_ferror = axis_setup["FERROR"]
            for joint, joint_setup in joints.items():
                max_velocity = joint_setup["MAX_VELOCITY"]
                max_acceleration = joint_setup["MAX_ACCELERATION"]
                min_limit = joint_setup["MIN_LIMIT"]
                max_limit = joint_setup["MAX_LIMIT"]
                backlash = joint_setup.get("BACKLASH", 0.0)
                ferror = joint_setup.get("FERROR", axis_ferror)
                if axis_max_velocity > max_velocity:
                    axis_max_velocity = max_velocity
                if axis_max_acceleration > max_acceleration:
                    axis_max_acceleration = max_acceleration
                if axis_min_limit > min_limit:
                    axis_min_limit = min_limit
                if axis_max_limit < max_limit:
                    axis_max_limit = max_limit

                if axis_backlash < backlash:
                    axis_backlash = backlash
                if axis_ferror < ferror:
                    axis_ferror = ferror

                axis_setup["MAX_VELOCITY"] = axis_max_velocity
                axis_setup["MAX_ACCELERATION"] = axis_max_acceleration
                axis_setup["MIN_LIMIT"] = axis_min_limit
                axis_setup["MAX_LIMIT"] = axis_max_limit
                axis_setup["BACKLASH"] = axis_backlash
                axis_setup["FERROR"] = axis_ferror
                if gui == "qtplasmac":
                    axis_setup["OFFSET_AV_RATIO"] = 0.5

                for key in axis_setup:
                    if key in axis_config:
                        axis_setup[key] = axis_config[key]

            for key, value in axis_setup.items():
                if key.endswith("_VELOCITY") and "ANGULAR" not in key:
                    output.append(f"# {value} * 60.0 = {float(value) * 60.0:0.1f} units/min")
                output.append(f"{key:18s} = {value}")
            output.append("")
            for joint, joint_config in joints.items():
                position_mode = joint_config["position_mode"]
                position_halname = joint_config["position_halname"]
                feedback_halname = joint_config["feedback_halname"]
                plugin_instance = joint_config["plugin_instance"]

                output.append(f"[JOINT_{joint}]")
                output.append(f"# {plugin_instance.instances_name}")
                if position_mode == "absolute":
                    for key, value in joint_config.items():
                        if key in self.JOINT_DEFAULTS:
                            output.append(f"{key:18s} = {value}")

                elif position_halname and feedback_halname:
                    pid_setup = self.PID_DEFAULTS.copy()
                    for key, value in pid_setup.items():
                        setup_value = joint_config.get(f"PID_{key.upper()}")
                        if setup_value:
                            value = setup_value
                        output.append(f"{key:18s} = {value}")
                    output.append("")
                    for key, value in joint_config.items():
                        if key in self.JOINT_DEFAULTS:
                            if key.endswith("_VELOCITY"):
                                output.append(f"# {value} * 60.0 = {float(value) * 60.0:0.1f} units/min")
                            output.append(f"{key:18s} = {value}")
                output.append("")

        path_subroutines = ini_setup.get("RS274NGC", {}).get("SUBROUTINE_PATH")
        if path_subroutines and path_subroutines.startswith("./"):
            os.makedirs(os.path.join(self.configuration_path, path_subroutines), exist_ok=True)
            for subroutine in glob.glob(os.path.join(json_path, "subroutines", "*")):
                target_path = os.path.join(self.configuration_path, path_subroutines, os.path.basename(subroutine))
                if not os.path.isfile(target_path):
                    shutil.copy(subroutine, target_path)

        path_mcodes = ini_setup.get("RS274NGC", {}).get("USER_M_PATH")
        if path_mcodes and path_mcodes.startswith("./"):
            os.makedirs(os.path.join(self.configuration_path, path_mcodes), exist_ok=True)
            for mcode in glob.glob(os.path.join(json_path, "mcodes", "*")):
                target_path = os.path.join(self.configuration_path, path_mcodes, os.path.basename(mcode))
                if not os.path.isfile(target_path):
                    shutil.copy(mcode, target_path)

        os.makedirs(self.configuration_path, exist_ok=True)
        open(os.path.join(self.configuration_path, "rio.ini"), "w").write("\n".join(output))

    def misc(self):
        if not os.path.isfile(os.path.join(self.configuration_path, "tool.tbl")):
            tooltbl = []
            tooltbl.append("T1 P1 D0.125000 Z+0.511000 ;1/8 end mill")
            tooltbl.append("T2 P2 D0.062500 Z+0.100000 ;1/16 end mill")
            tooltbl.append("T3 P3 D0.201000 Z+1.273000 ;#7 tap drill")
            os.makedirs(self.configuration_path, exist_ok=True)
            open(os.path.join(self.configuration_path, "tool.tbl"), "w").write("\n".join(tooltbl))

    def riof(self):
        linuxcnc_config = self.project.config["jdata"].get("linuxcnc", {})
        gui = linuxcnc_config.get("gui", "axis")

        # scale and offset
        for plugin_instance in self.project.plugin_instances:
            if plugin_instance.plugin_setup.get("is_joint", False) is False:
                for signal_name, signal_config in plugin_instance.signals().items():
                    halname = signal_config["halname"]
                    netname = signal_config["netname"]
                    userconfig = signal_config.get("userconfig")
                    scale = userconfig.get("scale")
                    offset = userconfig.get("offset")
                    setp = userconfig.get("setp")
                    if not netname and setp is not None:
                        if scale:
                            self.halg.setp_add(f"rio.{halname}-scale", scale)
                        if offset:
                            self.halg.setp_add(f"rio.{halname}-offset", offset)

        # rio-functions
        self.rio_functions = {}
        for plugin_instance in self.project.plugin_instances:
            if plugin_instance.plugin_setup.get("is_joint", False) is False:
                for signal_name, signal_config in plugin_instance.signals().items():
                    halname = signal_config["halname"]
                    netname = signal_config["netname"]
                    virtual = signal_config.get("virtual")
                    userconfig = signal_config.get("userconfig")
                    function = userconfig.get("function", "")
                    rio_function = function.split(".", 1)
                    if function and rio_function[0] in {"jog"}:
                        if rio_function[0] not in self.rio_functions:
                            self.rio_functions[rio_function[0]] = {}
                        self.rio_functions[rio_function[0]][rio_function[1]] = halname
                    elif function and rio_function[0] in {"wcomp"}:
                        if rio_function[0] not in self.rio_functions:
                            self.rio_functions[rio_function[0]] = {}
                        values = rio_function[1].split(".")
                        vmin = values[0]
                        vmax = values[-1]
                        self.rio_functions[rio_function[0]][halname] = {
                            "source": halname,
                            "vmin": vmin,
                            "vmax": vmax,
                            "virtual": virtual,
                        }

        if "wcomp" in self.rio_functions:
            self.halg.fmt_add("")
            self.halg.fmt_add("# wcomp")
            for function, halname in self.rio_functions["wcomp"].items():
                source = halname["source"]
                vmin = halname["vmin"]
                vmax = halname["vmax"]
                virtual = halname["virtual"]
                self.halg.fmt_add(f"loadrt wcomp names=riof.{source}")
                self.halg.fmt_add(f"addf riof.{source} servo-thread")
                self.halg.setp_add(f"riof.{source}.min", vmin)
                self.halg.setp_add(f"riof.{source}.max", vmax)
                if virtual:
                    self.halg.net_add(f"riov.{source}", f"riof.{source}.in")
                else:
                    self.halg.net_add(f"rio.{source}", f"riof.{source}.in")

        if "jog" in self.rio_functions:
            self.halg.fmt_add("")
            self.halg.fmt_add("# Jogging")
            speed_selector = False
            axis_selector = False
            axis_leds = False
            axis_move = False
            wheel = False
            position_display = False
            for function, halname in self.rio_functions["jog"].items():
                if function.startswith("select-"):
                    axis_selector = True
                elif function.startswith("selected-"):
                    axis_leds = True
                elif function in {"plus", "minus"}:
                    axis_move = True
                elif function in {"fast"}:
                    speed_selector = True
                elif function in {"speed0"}:
                    speed_selector = True
                elif function in {"speed1"}:
                    speed_selector = True
                elif function in {"position"}:
                    position_display = True
                elif function in {"wheel"}:
                    wheel = True

            riof_jog_default = self.project.config["jdata"].get("linuxcnc", {}).get("rio_functions", {}).get("jog", {})

            def riof_jog_setup(section, key):
                return riof_jog_default.get(section, {}).get(key, halpins.RIO_FUNCTION_DEFAULTS["jog"][section][key]["default"])

            wheel_scale = riof_jog_setup("wheel", "scale")

            if speed_selector:
                wheel_scale = None

                speed_selector_mux = 1
                for function, halname in self.rio_functions["jog"].items():
                    if function == "speed0":
                        speed_selector_mux *= 2
                    elif function == "speed1":
                        speed_selector_mux *= 2
                    elif function == "fast":
                        speed_selector_mux *= 2

                # TODO: using mux-gen ?
                if speed_selector_mux > 4:
                    print("ERROR: only two speed selectors are supported")
                    speed_selector_mux = 4
                elif speed_selector_mux == 1:
                    print("ERROR: no speed selectors found")

                if speed_selector_mux in {2, 4}:
                    self.halg.fmt_add(f"loadrt mux{speed_selector_mux} names=riof.jog.wheelscale_mux")
                    self.halg.fmt_add("addf riof.jog.wheelscale_mux servo-thread")

                    self.halg.setp_add("riof.jog.wheelscale_mux.in0", riof_jog_setup("wheel", "scale_0"))
                    self.halg.setp_add("riof.jog.wheelscale_mux.in1", riof_jog_setup("wheel", "scale_1"))
                    if speed_selector_mux == 4:
                        self.halg.setp_add("riof.jog.wheelscale_mux.in2", riof_jog_setup("wheel", "scale_2"))
                        self.halg.setp_add("riof.jog.wheelscale_mux.in3", riof_jog_setup("wheel", "scale_3"))

                    in_n = 0
                    for function, halname in self.rio_functions["jog"].items():
                        if function in {"fast", "speed0", "speed1"}:
                            if speed_selector_mux == 2:
                                self.halg.net_add(f"rio.{halname}", "riof.jog.wheelscale_mux.sel")
                            else:
                                self.halg.net_add(f"rio.{halname}", f"riof.jog.wheelscale_mux.sel{in_n}")
                                in_n += 1

                    # pname = self.gui_gen.draw_number("Jogscale", "jogscale")
                    # self.halg.net_add("riof.jog.wheelscale_mux.out", pname)

            if wheel:
                halname_wheel = ""
                for function, halname in self.rio_functions["jog"].items():
                    if function == "wheel":
                        halname_wheel = f"rio.{halname}-s32"
                        break

                wheelfilter = riof_jog_setup("wheel", "filter")
                if halname_wheel and wheelfilter:
                    wf_gain = riof_jog_setup("wheel", "filter_gain")
                    wf_scale = riof_jog_setup("wheel", "filter_scale")
                    self.halg.fmt_add("loadrt ilowpass names=riof.jog.wheelilowpass")
                    self.halg.fmt_add("addf riof.jog.wheelilowpass servo-thread")
                    self.halg.setp_add("riof.jog.wheelilowpass.gain", wf_gain)
                    self.halg.setp_add("riof.jog.wheelilowpass.scale", wf_scale)
                    self.halg.net_add(halname_wheel, "riof.jog.wheelilowpass.in")
                    halname_wheel = "riof.jog.wheelilowpass.out"

                if halname_wheel:
                    for axis_name, axis_config in self.axis_dict.items():
                        joints = axis_config["joints"]
                        laxis = axis_name.lower()
                        self.halg.setp_add(f"axis.{laxis}.jog-vel-mode", 1)

                        if wheel_scale is not None:
                            self.halg.setp_add(f"axis.{laxis}.jog-scale", wheel_scale)
                        else:
                            self.halg.net_add("riof.jog.wheelscale_mux.out", f"axis.{laxis}.jog-scale")

                        if gui == "axis":
                            self.halg.net_add(f"axisui.jog.{laxis}", f"axis.{laxis}.jog-enable", f"jog-{laxis}-enable")
                            self.halg.net_add(halname_wheel, f"axis.{laxis}.jog-counts", f"jog-{laxis}-counts")
                            for joint, joint_setup in joints.items():
                                self.halg.setp_add(f"joint.{joint}.jog-vel-mode", 1)

                                if wheel_scale is not None:
                                    self.halg.setp_add(f"joint.{joint}.jog-scale", wheel_scale)
                                else:
                                    self.halg.net_add("riof.jog.wheelscale_mux.out", f"joint.{joint}.jog-scale")

                                self.halg.net_add(f"axisui.jog.{laxis}", f"joint.{joint}.jog-enable", f"jog-{joint}-enable")
                                self.halg.net_add(halname_wheel, f"joint.{joint}.jog-counts", f"jog-{joint}-counts")

            else:
                for axis_name, axis_config in self.axis_dict.items():
                    joints = axis_config["joints"]
                    laxis = axis_name.lower()
                    fname = f"wheel_{laxis}"
                    if fname in self.rio_functions["jog"]:
                        self.halg.setp_add(f"axis.{laxis}.jog-vel-mode", 1)

                        if wheel_scale is not None:
                            self.halg.setp_add(f"axis.{laxis}.jog-scale", wheel_scale)
                        else:
                            self.halg.net_add("riof.jog.wheelscale_mux.out", f"axis.{laxis}.jog-scale")

                        self.halg.setp_add(f"axis.{laxis}.jog-enable", 1)
                        for function, halname in self.rio_functions["jog"].items():
                            if function == fname:
                                self.halg.net_add(f"rio.{halname}-s32", f"axis.{laxis}.jog-counts", f"jog-{laxis}-counts")

                        for joint, joint_setup in joints.items():
                            self.halg.setp_add(f"joint.{joint}.jog-vel-mode", 1)

                            if wheel_scale is not None:
                                self.halg.setp_add(f"joint.{joint}.jog-scale", wheel_scale)
                            else:
                                self.halg.net_add("riof.jog.wheelscale_mux.out", f"joint.{joint}.jog-scale")

                            self.halg.setp_add(f"joint.{joint}.jog-enable", 1)
                            for function, halname in self.rio_functions["jog"].items():
                                if function == fname:
                                    self.halg.net_add(f"rio.{halname}-s32", f"joint.{joint}.jog-counts", f"jog-{joint}-counts")

            if speed_selector:
                speed_selector_mux = 1

                for function, halname in self.rio_functions["jog"].items():
                    if function == "speed0":
                        speed_selector_mux *= 2
                    elif function == "speed1":
                        speed_selector_mux *= 2
                    elif function == "fast":
                        speed_selector_mux *= 2

                if speed_selector_mux > 4:
                    print("ERROR: only two speed selectors are supported")
                    speed_selector_mux = 4
                elif speed_selector_mux == 1:
                    print("ERROR: no speed selectors found")

                if speed_selector_mux in {2, 4}:
                    self.halg.fmt_add(f"loadrt mux{speed_selector_mux} names=riof.jog.speed_mux")
                    self.halg.fmt_add("addf riof.jog.speed_mux servo-thread")

                    if speed_selector_mux == 2:
                        self.halg.setp_add("riof.jog.speed_mux.in0", riof_jog_setup("keys", "speed_0"))
                        self.halg.setp_add("riof.jog.speed_mux.in1", riof_jog_setup("keys", "speed_1"))
                    else:
                        self.halg.setp_add("riof.jog.speed_mux.in0", riof_jog_setup("keys", "speed_0"))
                        self.halg.setp_add("riof.jog.speed_mux.in1", riof_jog_setup("keys", "speed_1"))
                        self.halg.setp_add("riof.jog.speed_mux.in2", riof_jog_setup("keys", "speed_2"))
                        self.halg.setp_add("riof.jog.speed_mux.in3", riof_jog_setup("keys", "speed_3"))

                    in_n = 0
                    for function, halname in self.rio_functions["jog"].items():
                        if function in {"fast", "speed0", "speed1"}:
                            if speed_selector_mux == 2:
                                self.halg.net_add(f"rio.{halname}", "riof.jog.speed_mux.sel")
                            else:
                                self.halg.net_add(f"rio.{halname}", f"riof.jog.speed_mux.sel{in_n}")
                                in_n += 1

                    # pname = self.gui_gen.draw_number("Jogspeed", "jogspeed")
                    # self.halg.net_add("riof.jog.speed_mux.out", pname)
                    self.halg.net_add("riof.jog.speed_mux.out", "halui.axis.jog-speed")
                    self.halg.net_add("riof.jog.speed_mux.out", "halui.joint.jog-speed")
            else:
                self.halg.setp_add("halui.axis.jog-speed", riof_jog_setup("keys", "speed"))
                self.halg.setp_add("halui.joint.jog-speed", riof_jog_setup("keys", "speed"))

            if axis_move:
                for function, halname in self.rio_functions["jog"].items():
                    if function in {"plus", "minus"}:
                        self.halg.net_add(f"rio.{halname}", f"halui.joint.selected.{function}")
                        self.halg.net_add(f"rio.{halname}", f"halui.axis.selected.{function}")

            if axis_selector:
                joint_n = 0
                for function, halname in self.rio_functions["jog"].items():
                    if function.startswith("select-"):
                        axis_name = function.split("-")[-1]
                        self.halg.net_add(f"rio.{halname}", f"halui.axis.{axis_name}.select")
                        self.halg.net_add(f"rio.{halname}", f"halui.joint.{joint_n}.select")
                        pname = self.gui_gen.draw_led(f"Jog:{axis_name}", f"selected-{axis_name}")
                        self.halg.net_add(f"halui.axis.{axis_name}.is-selected", pname)
                        for axis_id, axis_config in self.axis_dict.items():
                            joints = axis_config["joints"]
                            laxis = axis_id.lower()
                            if axis_name == laxis:
                                self.halg.fmt_add("")
                                self.halg.fmt_add(f"# axis {laxis} selection")
                                self.halg.fmt_add(f"loadrt oneshot names=riof.axisui-{laxis}-oneshot")
                                self.halg.fmt_add(f"addf riof.axisui-{laxis}-oneshot servo-thread")
                                self.halg.setp_add(f"riof.axisui-{laxis}-oneshot.width", 0.1)
                                self.halg.setp_add(f"riof.axisui-{laxis}-oneshot.retriggerable", 0)
                                if gui == "axis":
                                    self.halg.net_add(f"axisui.jog.{laxis}", f"riof.axisui-{laxis}-oneshot.in")
                                    self.halg.net_add(f"riof.axisui-{laxis}-oneshot.out", f"halui.axis.{laxis}.select")
                                    for joint, joint_setup in joints.items():
                                        self.halg.net_add(f"riof.axisui-{laxis}-oneshot.out", f"halui.joint.{joint}.select")
                        joint_n += 1
            else:
                for axis_id, axis_config in self.axis_dict.items():
                    joints = axis_config["joints"]
                    laxis = axis_id.lower()
                    self.halg.fmt_add("")
                    self.halg.fmt_add(f"# axis {laxis} selection")
                    self.halg.fmt_add(f"loadrt oneshot names=riof.axisui-{laxis}-oneshot")
                    self.halg.fmt_add(f"addf riof.axisui-{laxis}-oneshot servo-thread")
                    self.halg.setp_add(f"riof.axisui-{laxis}-oneshot.width", 0.1)
                    self.halg.setp_add(f"riof.axisui-{laxis}-oneshot.retriggerable", 0)
                    if gui == "axis":
                        self.halg.net_add(f"axisui.jog.{laxis}", f"riof.axisui-{laxis}-oneshot.in")
                        self.halg.net_add(f"riof.axisui-{laxis}-oneshot.out", f"halui.axis.{laxis}.select")
                        for joint, joint_setup in joints.items():
                            self.halg.net_add(f"riof.axisui-{laxis}-oneshot.out", f"halui.joint.{joint}.select")

            if axis_selector and position_display:
                self.halg.fmt_add("")
                self.halg.fmt_add("# display position")
                self.halg.fmt_add("loadrt mux16 names=riof.jog.position_mux")
                self.halg.fmt_add("addf riof.jog.position_mux servo-thread")
                mux_select = 0
                mux_input = 1
                for function, halname in self.rio_functions["jog"].items():
                    if function.startswith("select-"):
                        axis_name = function.split("-")[-1]
                        self.halg.net_add(f"halui.axis.{axis_name}.is-selected", f"riof.jog.position_mux.sel{mux_select}")
                        self.halg.net_add(f"halui.axis.{axis_name}.pos-relative", f"riof.jog.position_mux.in{mux_input:02d}")
                        mux_select += 1
                        mux_input = mux_input * 2
                    elif function == "position":
                        self.halg.net_add("riof.jog.position_mux.out-f", f"rio.{halname}")

            if axis_leds:
                for function, halname in self.rio_functions["jog"].items():
                    if function.startswith("selected-"):
                        axis_name = function.split("-")[-1]
                        self.halg.net_add(f"halui.axis.{axis_name}.is-selected", f"rio.{halname}")

    def gui(self):
        os.makedirs(self.configuration_path, exist_ok=True)
        linuxcnc_config = self.project.config["jdata"].get("linuxcnc", {})
        machinetype = linuxcnc_config.get("machinetype")
        embed_vismach = linuxcnc_config.get("embed_vismach")
        vcp_sections = linuxcnc_config.get("vcp_sections", [])
        vcp_mode = linuxcnc_config.get("vcp_mode", "ALL")
        vcp_pos = linuxcnc_config.get("vcp_pos", "RIGHT")
        gui = linuxcnc_config.get("gui", "axis")
        ini_setup = self.ini_defaults(self.project.config["jdata"], num_joints=self.num_joints, axis_dict=self.axis_dict, gui_type=self.gui_type)

        if not self.gui_gen:
            return

        self.gui_gen.draw_begin(self.gui_prefix, vcp_pos=vcp_pos)

        # build complete list of sections (in right order)
        for plugin_instance in self.project.plugin_instances:
            if plugin_instance.plugin_setup.get("is_joint", False) is False:
                for signal_name, signal_config in plugin_instance.signals().items():
                    userconfig = signal_config.get("userconfig", {})
                    displayconfig = userconfig.get("display", signal_config.get("display", {}))
                    section = displayconfig.get("section", "").lower()
                    if section and section not in vcp_sections:
                        vcp_sections.append(section)
        for section in ("status", "inputs", "outputs", "virtual"):
            if section not in vcp_sections:
                vcp_sections.append(section)
        self.gui_gen.draw_tabs_begin([tab.title() for tab in vcp_sections])

        # analyse halnames to generate titles
        prefixes = {}
        haltitles = {}
        for plugin_instance in self.project.plugin_instances:
            if plugin_instance.plugin_setup.get("is_joint", False) is False:
                for signal_name, signal_config in plugin_instance.signals().items():
                    halname = signal_config["halname"]
                    prefix = ".".join(halname.split(".")[:-1])
                    if prefix not in prefixes:
                        prefixes[prefix] = []
                    prefixes[prefix].append(halname)
        for prefix, halnames in prefixes.items():
            if len(halnames) == 1:
                for halname in halnames:
                    haltitles[halname] = prefix.title()

        # generate tab (vcp) for each section
        for tab in vcp_sections:
            self.gui_gen.draw_tab_begin(tab.title())

            if tab == "status":
                if machinetype == "melfa":
                    if hasattr(self.gui_gen, "draw_multilabel"):
                        pname = self.gui_gen.draw_multilabel("kinstype", "kinstype", setup={"legends": ["WORLD COORD", "JOINT COORD"]})
                        self.halg.net_add("kinstype.is-0", f"{pname}.legend0")
                        self.halg.net_add("kinstype.is-1", f"{pname}.legend1")
                    pname = self.gui_gen.draw_button("Clear Path", "vismach-clear")

                    self.gui_gen.draw_hbox_begin()

                    if embed_vismach:
                        self.halg.net_add(pname, f"{embed_vismach}.plotclear")
                    else:
                        self.halg.net_add(pname, "vismach.plotclear")

                    for joint in range(6):
                        pname = self.gui_gen.draw_meter(f"Joint{joint + 1}", f"joint_pos{joint}", setup={"size": 100, "min": -360, "max": 360})
                        self.halg.net_add(f"joint.{joint}.pos-fb", pname)
                        if joint == 2:
                            self.gui_gen.draw_hbox_end()
                            self.gui_gen.draw_hbox_begin()

                    self.gui_gen.draw_hbox_end()

                # buttons
                self.gui_gen.draw_frame_begin("MDI-Commands")
                self.gui_gen.draw_vbox_begin()

                mdi_num = 0
                mdi_group_last = None
                for mdi_num, command in enumerate(ini_setup["HALUI"]):
                    if command.startswith("MDI_COMMAND|"):
                        # grouping mdi's in hbox
                        mdi_group = None
                        if len(command.split("|")) == 4:
                            mdi_group = command.split("|")[2]
                        if mdi_group != mdi_group_last:
                            if mdi_group is not None:
                                if mdi_group_last is not None:
                                    self.gui_gen.draw_hbox_end()
                                    self.gui_gen.draw_frame_end()
                                self.gui_gen.draw_frame_begin(mdi_group)
                                self.gui_gen.draw_hbox_begin()
                            else:
                                self.gui_gen.draw_hbox_end()
                                self.gui_gen.draw_frame_end()
                        mdi_title = command.split("|")[-1]
                        halpin = f"halui.mdi-command-{mdi_num:02d}"
                        pname = self.gui_gen.draw_button(mdi_title, halpin)
                        self.halg.net_add(pname, halpin)
                        mdi_group_last = mdi_group

                if mdi_group_last is not None:
                    self.gui_gen.draw_hbox_end()
                    self.gui_gen.draw_frame_end()

                self.gui_gen.draw_vbox_end()
                self.gui_gen.draw_frame_end()

            for plugin_instance in self.project.plugin_instances:
                if plugin_instance.plugin_setup.get("is_joint", False) is False:
                    for signal_name, signal_config in plugin_instance.signals().items():
                        halname = signal_config["halname"]
                        netname = signal_config["netname"]
                        direction = signal_config["direction"]
                        userconfig = signal_config.get("userconfig", {})
                        boolean = signal_config.get("bool")
                        virtual = signal_config.get("virtual")
                        setp = userconfig.get("setp")
                        function = userconfig.get("function", "")
                        displayconfig = userconfig.get("display", signal_config.get("display", {}))
                        if function and not virtual:
                            continue
                        if signal_config.get("helper", False) and not displayconfig:
                            continue
                        vmin = signal_config.get("min", -1000)
                        vmax = signal_config.get("max", 1000)
                        vformat = signal_config.get("format")
                        vunit = signal_config.get("unit")
                        if "min" not in displayconfig:
                            displayconfig["min"] = vmin
                        if "max" not in displayconfig:
                            displayconfig["max"] = vmax
                        if vformat and "format" not in displayconfig:
                            displayconfig["format"] = vformat
                        if vunit and "unit" not in displayconfig:
                            displayconfig["unit"] = vunit

                        if setp:
                            continue

                        if halname in self.feedbacks:
                            continue

                        dtype = None
                        if (netname and not virtual) or setp:
                            if direction == "input":
                                section = displayconfig.get("section", "inputs").lower()
                            elif direction == "output":
                                section = displayconfig.get("section", "outputs").lower()
                            if not boolean:
                                dtype = displayconfig.get("type", "number")
                            else:
                                dtype = displayconfig.get("type", "led")

                        elif virtual:
                            section = displayconfig.get("section", "virtual").lower()
                            if direction == "output":
                                if not boolean:
                                    dtype = displayconfig.get("type", "number")
                                else:
                                    dtype = displayconfig.get("type", "led")
                            elif direction == "input":
                                if not boolean:
                                    dtype = displayconfig.get("type", "scale")
                                else:
                                    dtype = displayconfig.get("type", "checkbutton")

                        elif direction == "input":
                            section = displayconfig.get("section", "inputs").lower()
                            if not boolean:
                                dtype = displayconfig.get("type", "number")
                            else:
                                dtype = displayconfig.get("type", "led")
                        elif direction == "output":
                            section = displayconfig.get("section", "outputs").lower()
                            if not boolean:
                                dtype = displayconfig.get("type", "scale")
                            else:
                                dtype = displayconfig.get("type", "checkbutton")

                        if vcp_mode == "CONFIGURED" and not displayconfig.get("type") and not displayconfig.get("title"):
                            continue

                        if section != tab:
                            continue

                        if hasattr(self.gui_gen, f"draw_{dtype}"):
                            title = haltitles.get(halname, halname)
                            gui_pinname = getattr(self.gui_gen, f"draw_{dtype}")(title, halname, setup=displayconfig)

                            # fselect handling
                            if dtype == "fselect":
                                values = displayconfig.get("values", {"v0": 0, "v1": 1})
                                n_values = len(values)
                                self.halextras.append(f"loadrt conv_s32_u32 names=conv_s32_u32_{halname}")
                                self.halextras.append(f"addf conv_s32_u32_{halname} servo-thread")
                                self.halg.net_add(f"{gui_pinname}-i", f"conv_s32_u32_{halname}.in")
                                self.halextras.append("")
                                self.halextras.append(f"loadrt demux names=demux_{halname} personality={n_values}")
                                self.halextras.append(f"addf demux_{halname} servo-thread")
                                self.halg.net_add(f"conv_s32_u32_{halname}.out", f"demux_{halname}.sel-u32")
                                for nv in range(n_values):
                                    self.halg.net_add(f"demux_{halname}.out-{nv:02d}", f"{gui_pinname}-label.legend{nv}")
                                self.halextras.append("")
                                self.halextras.append(f"loadrt bitslice names=bitslice_{halname} personality=3")
                                self.halextras.append(f"addf bitslice_{halname} servo-thread")
                                self.halg.net_add(f"conv_s32_u32_{halname}.out", f"bitslice_{halname}.in")
                                self.halextras.append("")
                                self.halextras.append(f"loadrt mux8 names=mux8_{halname}")
                                self.halextras.append(f"addf mux8_{halname} servo-thread")
                                self.halg.net_add(f"bitslice_{halname}.out-00", f"mux8_{halname}.sel0")
                                self.halg.net_add(f"bitslice_{halname}.out-01", f"mux8_{halname}.sel1")
                                self.halg.net_add(f"bitslice_{halname}.out-02", f"mux8_{halname}.sel2")
                                for vn, name in enumerate(values):
                                    self.halg.setp_add(f"mux8_{halname}.in{vn}", values[name])
                                self.halextras.append("")
                                gui_pinname = f"mux8_{halname}.out"

                            if direction == "input":
                                dfilter = displayconfig.get("filter", {})
                                dfilter_type = dfilter.get("type")
                                if dfilter_type == "LOWPASS":
                                    dfilter_gain = dfilter.get("gain", "0.001")
                                    self.halextras.append(f"loadrt lowpass names=lowpass_{halname}")
                                    self.halextras.append(f"addf lowpass_{halname} servo-thread")
                                    self.halg.setp_add(f"lowpass_{halname}.load", 0)
                                    self.halg.setp_add(f"lowpass_{halname}.gain", dfilter_gain)
                                    self.halg.net_add(gui_pinname, f"lowpass_{halname}.in")
                                    gui_pinname = f"lowpass_{halname}.out"

                            if virtual and direction == "input":
                                self.halg.net_add(gui_pinname, f"riov.{halname}", f"sig_riov_{halname.replace('.', '_')}")
                            elif virtual and direction == "output":
                                self.halg.net_add(f"riov.{halname}", gui_pinname, f"sig_riov_{halname.replace('.', '_')}")
                            elif netname or setp or direction == "input":
                                self.halg.net_add(f"rio.{halname}", gui_pinname)
                            elif direction == "output":
                                self.halg.net_add(gui_pinname, f"rio.{halname}")

                        elif dtype != "none":
                            print(f"WARNING: 'draw_{dtype}' not found")

            self.gui_gen.draw_tab_end()

        self.gui_gen.draw_tabs_end()
        self.gui_gen.draw_end()
        self.gui_gen.save(self.configuration_path)

    def hal(self):
        linuxcnc_config = self.project.config["jdata"].get("linuxcnc", {})
        gui = linuxcnc_config.get("gui", "axis")
        machinetype = linuxcnc_config.get("machinetype")
        embed_vismach = linuxcnc_config.get("embed_vismach")
        toolchange = linuxcnc_config.get("toolchange", "manual")

        self.halg = hal_generator()

        self.halg.fmt_add_top("# load the realtime components")
        self.halg.fmt_add_top("loadrt [KINS]KINEMATICS")
        self.halg.fmt_add_top(
            "loadrt [EMCMOT]EMCMOT base_period_nsec=[EMCMOT]BASE_PERIOD servo_period_nsec=[EMCMOT]SERVO_PERIOD num_joints=[KINS]JOINTS num_dio=[EMCMOT]NUM_DIO num_aio=[EMCMOT]NUM_AIO"
        )
        self.halg.fmt_add_top("loadrt rio")
        self.halg.fmt_add_top("")
        self.halg.fmt_add_top("# if you need to test rio without hardware, set it to 1")
        self.halg.fmt_add_top("setp rio.sys-simulation 0")
        self.halg.fmt_add_top("")

        num_pids = self.num_joints
        self.halg.fmt_add_top(f"loadrt pid num_chan={num_pids}")
        for pidn in range(num_pids):
            self.halg.fmt_add_top(f"addf pid.{pidn}.do-pid-calcs servo-thread")
        self.halg.fmt_add_top("")

        self.halg.fmt_add_top("# add the rio and motion functions to threads")
        self.halg.fmt_add_top("addf motion-command-handler servo-thread")
        self.halg.fmt_add_top("addf motion-controller servo-thread")
        self.halg.fmt_add_top("addf rio.readwrite servo-thread")
        self.halg.fmt_add_top("")
        self.halg.net_add("iocontrol.0.user-enable-out", "rio.sys-enable", "user-enable-out")
        self.halg.net_add("iocontrol.0.user-request-enable", "rio.sys-enable-request", "user-request-enable")
        self.halg.net_add("rio.sys-status", "iocontrol.0.emc-enable-in")

        if gui not in {"qtdragon", "qtdragon_hd"}:
            if toolchange == "manual":
                if gui == "gmoccapy":
                    self.halg.net_add("iocontrol.0.tool-prep-number", "gmoccapy.toolchange-number", "tool-prep-number")
                    self.halg.net_add("iocontrol.0.tool-change", "gmoccapy.toolchange-change", "tool-change")
                    self.halg.net_add("gmoccapy.toolchange-changed", "iocontrol.0.tool-changed", "tool-changed")
                    self.halg.net_add("iocontrol.0.tool-prepare", "iocontrol.0.tool-prepared", "tool-prepared")
                else:
                    self.halg.fmt_add_top("loadusr -W hal_manualtoolchange")
                    self.halg.fmt_add_top("")
                    self.halg.net_add("iocontrol.0.tool-prep-number", "hal_manualtoolchange.number", "tool-prep-number")
                    self.halg.net_add("iocontrol.0.tool-change", "hal_manualtoolchange.change", "tool-change")
                    self.halg.net_add("hal_manualtoolchange.changed", "iocontrol.0.tool-changed", "tool-changed")
                    self.halg.net_add("iocontrol.0.tool-prepare", "iocontrol.0.tool-prepared", "tool-prepared")
            else:
                self.halg.net_add("iocontrol.0.tool-prepare", "iocontrol.0.tool-prepared", "tool-prepared")
                self.halg.net_add("iocontrol.0.tool-change", "iocontrol.0.tool-changed", "tool-changed")

        linuxcnc_setp = {}

        if machinetype == "corexy":
            self.halg.fmt_add_top("# machinetype is corexy")
            self.halg.fmt_add_top("loadrt corexy_by_hal names=corexy")
            self.halg.fmt_add_top("addf corexy servo-thread")
            self.halg.fmt_add_top("")
        elif machinetype == "ldelta":
            self.halg.fmt_add_top("# loading lineardelta gl-view")
            self.halg.fmt_add_top("loadusr -W lineardelta MIN_JOINT=-420")
            self.halg.fmt_add_top("")
        elif machinetype == "rdelta":
            self.halg.fmt_add_top("# loading rotarydelta gl-view")
            self.halg.fmt_add_top("loadusr -W rotarydelta MIN_JOINT=-420")
            self.halg.fmt_add_top("")
        elif machinetype == "melfa":
            if not embed_vismach:
                self.halg.fmt_add_top("# loading melfa gui")
                self.halg.fmt_add_top("loadusr -W melfagui")
                self.halg.fmt_add_top("")
            self.halg.fmt_add_top("net :kinstype-select <= motion.analog-out-03 => motion.switchkins-type")
            self.halg.fmt_add_top("")
            os.makedirs(self.configuration_path, exist_ok=True)

            for source in glob.glob(os.path.join(riocore_path, "files", "melfa", "*")):
                basename = os.path.basename(source)
                target = os.path.join(self.configuration_path, basename)
                if os.path.isfile(source):
                    shutil.copy(source, target)
                elif not os.path.isdir(target):
                    shutil.copytree(source, target)

            if not embed_vismach:
                for joint in range(6):
                    self.halg.net_add(f"joint.{joint}.pos-fb", f"melfagui.joint{joint + 1}")

            linuxcnc_setp = {
                "genserkins.A-0": 0,
                "genserkins.A-1": 85,
                "genserkins.A-2": 380,
                "genserkins.A-3": 100,
                "genserkins.A-4": 0,
                "genserkins.A-5": 0,
                "genserkins.ALPHA-0": 0,
                "genserkins.ALPHA-1": -1.570796326,
                "genserkins.ALPHA-2": 0,
                "genserkins.ALPHA-3": -1.570796326,
                "genserkins.ALPHA-4": 1.570796326,
                "genserkins.ALPHA-5": -1.570796326,
                "genserkins.D-0": 350,
                "genserkins.D-1": 0,
                "genserkins.D-2": 0,
                "genserkins.D-3": 425,
                "genserkins.D-4": 0,
                "genserkins.D-5": 235,
            }

        if embed_vismach:
            if embed_vismach in {"fanuc_200f"}:
                for joint in range(len(self.axis_dict)):
                    self.halg.net_add(f"joint.{joint}.pos-fb", f"{embed_vismach}.joint{joint + 1}")

        linuxcnc_setp.update(linuxcnc_config.get("setp", {}))
        for key, value in linuxcnc_setp.items():
            self.halg.setp_add(f"{key}", value)

        for addon_name, addon in self.addons.items():
            if hasattr(addon, "hal"):
                self.halg.fmt_add(addon.hal(self))

        for plugin_instance in self.project.plugin_instances:
            if plugin_instance.plugin_setup.get("is_joint", False) is False:
                for signal_name, signal_config in plugin_instance.signals().items():
                    halname = signal_config["halname"]
                    netname = signal_config["netname"]
                    userconfig = signal_config.get("userconfig", {})
                    scale = userconfig.get("scale")
                    offset = userconfig.get("offset")
                    setp = userconfig.get("setp")
                    direction = signal_config["direction"]
                    virtual = signal_config.get("virtual")
                    component = signal_config.get("component")
                    rprefix = "rio"
                    if virtual:
                        rprefix = "riov"

                    if scale and not virtual:
                        self.halg.setp_add(f"{rprefix}.{halname}-scale", scale)
                    if offset and not virtual:
                        self.halg.setp_add(f"{rprefix}.{halname}-offset", offset)

                    if netname:
                        if direction == "inout":
                            self.halg.fmt_add(f"net rios.{halname} {rprefix}.{halname} <=> {netname}")
                        elif direction == "input":
                            for net in netname.split(","):
                                net = net.strip()
                                net_type = halpins.LINUXCNC_SIGNALS[direction].get(net, {}).get("type", float)
                                if net_type is int:
                                    self.halg.net_add(f"{rprefix}.{halname}-s32", net)
                                else:
                                    self.halg.net_add(f"{rprefix}.{halname}", net)
                        elif direction == "output":
                            target = f"{rprefix}.{halname}"
                            self.halg.net_add(netname, f"{rprefix}.{halname}")
                    elif setp:
                        self.halg.setp_add(f"{rprefix}.{halname}", setp)
                    elif virtual and component:
                        if direction == "input":
                            self.halg.net_add(f"{rprefix}.{halname}", f"rio.{halname}")
                        else:
                            self.halg.net_add(f"rio.{halname}", f"{rprefix}.{halname}")

        for axis_name, axis_config in self.axis_dict.items():
            joints = axis_config["joints"]
            self.axisout.append(f"# Axis: {axis_name}")
            self.axisout.append("")
            for joint, joint_setup in joints.items():
                position_mode = joint_setup["position_mode"]
                position_halname = joint_setup["position_halname"]
                feedback_halname = joint_setup["feedback_halname"]
                enable_halname = joint_setup["enable_halname"]
                pin_num = joint_setup["pin_num"]
                if position_mode == "absolute":
                    self.axisout.append(f"# joint.{joint}: absolut positioning")
                    self.axisout.append(f"setp {position_halname}-scale [JOINT_{joint}]SCALE_OUT")
                    if machinetype == "corexy" and axis_name in {"X", "Y"}:
                        corexy_axis = "beta"
                        if axis_name == "X":
                            corexy_axis = "alpha"
                        self.axisout.append(f"net j{joint}pos-cmd <= joint.{joint}.motor-pos-cmd")
                        self.axisout.append(f"net j{joint}pos-cmd => corexy.j{joint}-motor-pos-cmd")
                        self.axisout.append(f"net j{joint}pos-cmd-{corexy_axis} <= corexy.{corexy_axis}-cmd")
                        self.axisout.append(f"net j{joint}pos-cmd-{corexy_axis} => {position_halname}")
                        self.axisout.append(f"net j{joint}pos-cmd => corexy.{corexy_axis}-fb")
                        self.axisout.append(f"net j{joint}pos-fb-{corexy_axis}  => corexy.j{joint}-motor-pos-fb")
                        self.axisout.append(f"net j{joint}pos-fb-{corexy_axis} => joint.{joint}.motor-pos-fb")
                    else:
                        self.axisout.append(f"net j{joint}pos-cmd <= joint.{joint}.motor-pos-cmd")
                        self.axisout.append(f"net j{joint}pos-cmd => {position_halname}")
                        self.axisout.append(f"net j{joint}pos-cmd => joint.{joint}.motor-pos-fb")
                    if enable_halname:
                        self.axisout.append(f"net j{joint}enable         <= joint.{joint}.amp-enable-out => {enable_halname}")
                elif position_halname and feedback_halname:
                    self.axisout.append(f"# joint.{joint}: relative positioning using pid.{pin_num}")
                    self.axisout.append(f"setp pid.{pin_num}.Pgain     [JOINT_{joint}]P")
                    self.axisout.append(f"setp pid.{pin_num}.Igain     [JOINT_{joint}]I")
                    self.axisout.append(f"setp pid.{pin_num}.Dgain     [JOINT_{joint}]D")
                    self.axisout.append(f"setp pid.{pin_num}.bias      [JOINT_{joint}]BIAS")
                    self.axisout.append(f"setp pid.{pin_num}.FF0       [JOINT_{joint}]FF0")
                    self.axisout.append(f"setp pid.{pin_num}.FF1       [JOINT_{joint}]FF1")
                    self.axisout.append(f"setp pid.{pin_num}.FF2       [JOINT_{joint}]FF2")
                    self.axisout.append(f"setp pid.{pin_num}.deadband  [JOINT_{joint}]DEADBAND")
                    self.axisout.append(f"setp pid.{pin_num}.maxoutput [JOINT_{joint}]MAXOUTPUT")
                    self.axisout.append(f"setp {position_halname}-scale [JOINT_{joint}]SCALE_OUT")
                    self.axisout.append(f"setp {feedback_halname}-scale [JOINT_{joint}]SCALE_IN")
                    if machinetype == "corexy" and axis_name in {"X", "Y"}:
                        corexy_axis = "beta"
                        if axis_name == "X":
                            corexy_axis = "alpha"
                        self.axisout.append(f"net j{joint}vel-cmd <= pid.{pin_num}.output")
                        self.axisout.append(f"net j{joint}vel-cmd => {position_halname}")
                        self.axisout.append(f"net j{joint}pos-cmd <= joint.{joint}.motor-pos-cmd")
                        self.axisout.append(f"net j{joint}pos-cmd => corexy.j{joint}-motor-pos-cmd")
                        self.axisout.append(f"net j{joint}pos-cmd-{corexy_axis} <= corexy.{corexy_axis}-cmd")
                        self.axisout.append(f"net j{joint}pos-cmd-{corexy_axis} => pid.{pin_num}.command")
                        self.axisout.append(f"net j{joint}pos-fb-{corexy_axis}  <= {feedback_halname}")
                        self.axisout.append(f"net j{joint}pos-fb-{corexy_axis}  => corexy.{corexy_axis}-fb")
                        self.axisout.append(f"net j{joint}pos-fb-{corexy_axis}  => pid.{joint}.feedback")
                        self.axisout.append(f"net j{joint}pos-fb  <= corexy.j{joint}-motor-pos-fb")
                        self.axisout.append(f"net j{joint}pos-fb  => joint.{joint}.motor-pos-fb")
                    else:
                        self.axisout.append(f"net j{joint}vel-cmd <= pid.{pin_num}.output")
                        self.axisout.append(f"net j{joint}vel-cmd => {position_halname}")
                        self.axisout.append(f"net j{joint}pos-cmd <= joint.{joint}.motor-pos-cmd")
                        self.axisout.append(f"net j{joint}pos-cmd => pid.{pin_num}.command")
                        self.axisout.append(f"net j{joint}pos-fb  <= {feedback_halname}")
                        self.axisout.append(f"net j{joint}pos-fb  => joint.{joint}.motor-pos-fb")
                        self.axisout.append(f"net j{joint}pos-fb  => pid.{joint}.feedback")

                    if machinetype in {"ldelta", "rdelta"} and axis_name in {"X", "Y", "Z", "XYZ"}:
                        self.axisout.append(f"net j{joint}pos-fb  => lineardelta.joint{joint}")

                    if enable_halname:
                        self.axisout.append(f"net j{joint}enable  <= joint.{joint}.amp-enable-out")
                        self.axisout.append(f"net j{joint}enable  => {enable_halname}")
                    else:
                        self.axisout.append(f"net j{joint}enable  <= joint.{joint}.amp-enable-out")
                    self.axisout.append(f"net j{joint}enable  => pid.{pin_num}.enable")
                self.axisout.append("")

    def create_axis_config(self):
        linuxcnc_config = self.project.config["jdata"].get("linuxcnc", {})
        machinetype = linuxcnc_config.get("machinetype")
        pin_num = 0
        self.num_joints = 0
        self.num_axis = 0
        self.axis_dict = {}

        if machinetype in {"melfa", "puma"}:
            self.AXIS_NAMES = ["X", "Y", "Z", "A", "B", "C"]

        named_axis = []
        for plugin_instance in self.project.plugin_instances:
            if plugin_instance.plugin_setup.get("is_joint"):
                axis_name = plugin_instance.plugin_setup.get("axis")
                if axis_name:
                    named_axis.append(axis_name)

        for plugin_instance in self.project.plugin_instances:
            if plugin_instance.plugin_setup.get("is_joint"):
                axis_name = plugin_instance.plugin_setup.get("axis")
                if not axis_name:
                    for name in self.AXIS_NAMES:
                        if name not in self.axis_dict and name not in named_axis:
                            axis_name = name
                            break
                if axis_name:
                    if axis_name not in self.axis_dict:
                        self.axis_dict[axis_name] = {"joints": {}}
                    feedback = plugin_instance.plugin_setup.get("joint", {}).get("feedback")
                    self.axis_dict[axis_name]["joints"][self.num_joints] = {
                        "type": plugin_instance.NAME,
                        "axis": axis_name,
                        "joint": self.num_joints,
                        "plugin_instance": plugin_instance,
                        "feedback": feedback or True,
                    }
                    if feedback:
                        self.feedbacks.append(feedback.replace(":", "."))
                    self.num_joints += 1

        self.num_axis = len(self.axis_dict)

        # getting all home switches
        joint_homeswitches = []
        for plugin_instance in self.project.plugin_instances:
            if plugin_instance.plugin_setup.get("is_joint", False) is False:
                for signal_name, signal_config in plugin_instance.signals().items():
                    userconfig = signal_config.get("userconfig")
                    net = userconfig.get("net")
                    if net and net.startswith("joint.") and net.endswith(".home-sw-in"):
                        joint_homeswitches.append(int(net.split(".")[1]))

        for axis_name, axis_config in self.axis_dict.items():
            joints = axis_config["joints"]
            # print(f"  # Axis: {axis_name}")
            for joint, joint_setup in joints.items():
                position_halname = None
                enable_halname = None
                position_mode = None
                joint_config = joint_setup["plugin_instance"].plugin_setup.get("joint", {})
                position_scale = float(joint_config.get("scale", joint_setup["plugin_instance"].SIGNALS.get("position", {}).get("scale", self.JOINT_DEFAULTS["SCALE_OUT"])))
                if machinetype == "lathe":
                    home_sequence_default = 2
                    if axis_name == "X":
                        home_sequence_default = 1

                elif machinetype == "melfa":
                    home_sequence_default = 2
                    if axis_name == "X":
                        home_sequence_default = 2
                    elif axis_name == "Y":
                        home_sequence_default = 1
                    elif axis_name == "Z":
                        home_sequence_default = 1
                    elif axis_name == "A":
                        home_sequence_default = 1
                    elif axis_name == "B":
                        home_sequence_default = 2
                    elif axis_name == "C":
                        home_sequence_default = 1

                else:
                    home_sequence_default = 2
                    if axis_name == "Z":
                        home_sequence_default = 1
                home_sequence = joint_config.get("home_sequence", home_sequence_default)
                if home_sequence == "auto":
                    home_sequence = home_sequence_default
                joint_signals = joint_setup["plugin_instance"].signals()
                velocity = joint_signals.get("velocity")
                position = joint_signals.get("position")
                dty = joint_signals.get("dty")
                enable = joint_signals.get("enable")
                if enable:
                    enable_halname = f"rio.{enable['halname']}"
                if velocity:
                    position_halname = f"rio.{velocity['halname']}"
                    position_mode = "relative"
                elif position:
                    position_halname = f"rio.{position['halname']}"
                    position_mode = "absolute"
                elif dty:
                    position_halname = f"rio.{dty['halname']}"
                    position_mode = "relative"

                feedback_scale = position_scale
                feedback_halname = None
                feedback = joint_config.get("feedback")
                feedback = joint_setup.get("feedback")
                if position_mode == "relative" and feedback is True:
                    feedback_halname = f"rio.{position['halname']}"
                    feedback_scale = position_scale
                elif position_mode == "relative":
                    if ":" in feedback:
                        fb_plugin_name, fb_signal_name = feedback.split(":")
                    else:
                        fb_plugin_name = feedback
                        fb_signal_name = "position"
                    found = False
                    for sub_instance in self.project.plugin_instances:
                        if sub_instance.title == fb_plugin_name:
                            for sub_signal_name, sub_signal_config in sub_instance.signals().items():
                                if fb_signal_name != sub_signal_name:
                                    continue
                                sub_direction = sub_signal_config["direction"]
                                if sub_direction != "input":
                                    print("ERROR: can not use this as feedback (no input signal):", sub_signal_config)
                                    exit(1)
                                feedback_halname = f"rio.{sub_signal_config['halname']}"
                                feedback_signal = feedback_halname.split(".")[-1]
                                feedback_scale = float(sub_signal_config["plugin_instance"].plugin_setup.get("signals", {}).get(feedback_signal, {}).get("scale", 1.0))
                                found = True
                                break
                    if not found:
                        print(f"ERROR: feedback {fb_plugin_name}->{fb_signal_name} for joint {joint} not found")
                        continue

                joint_setup["position_mode"] = position_mode
                joint_setup["position_halname"] = position_halname
                joint_setup["feedback_halname"] = feedback_halname
                joint_setup["enable_halname"] = enable_halname
                joint_setup["pin_num"] = pin_num
                if position_mode != "absolute":
                    pin_num += 1

                # copy defaults
                for key, value in self.JOINT_DEFAULTS.items():
                    joint_setup[key.upper()] = value

                # update defaults
                # if position_scale < 0.0:
                # joint_setup["HOME_SEARCH_VEL"] *= -1.0
                # joint_setup["HOME_LATCH_VEL"] *= -1.0
                # joint_setup["HOME_FINAL_VEL"] *= -1.0
                # joint_setup["HOME_OFFSET"] *= -1.0

                if machinetype not in {"scara", "melfa", "puma", "lathe"}:
                    if axis_name in {"Z"}:
                        joint_setup["HOME_SEARCH_VEL"] *= -1.0
                        joint_setup["HOME_LATCH_VEL"] *= -1.0
                        joint_setup["MAX_VELOCITY"] /= 3.0

                if joint not in joint_homeswitches:
                    joint_setup["HOME_SEARCH_VEL"] = 0.0
                    joint_setup["HOME_LATCH_VEL"] = 0.0
                    joint_setup["HOME_FINAL_VEL"] = 0.0
                    joint_setup["HOME_OFFSET"] = 0
                    joint_setup["HOME"] = 0.0
                    joint_setup["HOME_SEQUENCE"] = 0

                if machinetype in {"scara"}:
                    if axis_name in {"Z"}:
                        joint_setup["TYPE"] = "LINEAR"
                    else:
                        joint_setup["TYPE"] = "ANGULAR"
                elif machinetype in {"melfa", "puma"}:
                    joint_setup["TYPE"] = "ANGULAR"
                else:
                    if axis_name in {"A", "C", "B"}:
                        joint_setup["TYPE"] = "ANGULAR"
                    else:
                        joint_setup["TYPE"] = "LINEAR"

                # set autogen values
                joint_setup["SCALE_OUT"] = position_scale
                joint_setup["SCALE_IN"] = feedback_scale
                joint_setup["HOME_SEQUENCE"] = home_sequence

                # overwrite with user configuration
                for key, value in joint_config.items():
                    key = key.upper()
                    joint_setup[key] = value

            # overwrite axis configuration with user data
            for key, value in linuxcnc_config.get("axis", {}).get(axis_name, {}).items():
                key = key.upper()
                axis_config[key] = value
