import copy
import glob
import importlib
import os
import shutil
import stat

import riocore
from riocore import halpins
from riocore.generator.flexvcp import flexvcp
from riocore.generator.gladevcp import gladevcp
from riocore.generator.hal import hal_generator
from riocore.generator.pyvcp import pyvcp
from riocore.generator.qtpyvcp import qtpyvcp
from riocore.generator.qtvcp import qtvcp

riocore_path = os.path.dirname(os.path.dirname(__file__))


class LinuxCNC:
    AXIS_DEFAULTS = {
        "MAX_VELOCITY": 40.0,
        "MAX_ACCELERATION": 500.0,
        "MIN_LIMIT": -500,
        "MAX_LIMIT": 500,
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
        "MAXSATURATED": 0,
    }
    JOINT_DEFAULTS = {
        "TYPE": "LINEAR",
        "FERROR": 2.0,
        "MIN_LIMIT": -500.0,
        "MAX_LIMIT": 1500.0,
        "MAX_VELOCITY": 40.0,
        "MAX_ACCELERATION": 500.0,
        "SCALE_OUT": 320.0,
        "SCALE_IN": 320.0,
        "HOME_SEARCH_VEL": -30.0,
        "HOME_LATCH_VEL": 5.0,
        "HOME_FINAL_VEL": 100.0,
        "HOME_IGNORE_LIMITS": "YES",
        "HOME_USE_INDEX": "NO",
        "HOME_OFFSET": 0.0,
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
            "INCREMENTS": "50mm, 10mm, 5mm, 1mm, .5mm, .1mm, .05mm, .01mm",
            # feedrate
            "MAX_FEED_OVERRIDE": 5.0,
            "MIN_LINEAR_VELOCITY": 0.0,
            "MAX_LINEAR_VELOCITY": 45.0,
            "DEFAULT_LINEAR_VELOCITY": 40.0,
            "MIN_ANGULAR_VELOCITY": 0.0,
            "MAX_ANGULAR_VELOCITY": 5.0,
            "DEFAULT_ANGULAR_VELOCITY": 2.5,
            # spindle
            "SPINDLES": 1,
            "MIN_SPINDLE_OVERRIDE": 0.5,
            "MAX_SPINDLE_OVERRIDE": 2.0,
            "MIN_SPINDLE_SPEED": 0,
            "MAX_SPINDLE_SPEED": 22000,
            "DEFAULT_SPINDLE_SPEED": 6000,
            "MIN_SPINDLE_0_OVERRIDE": 0.5,
            "MAX_SPINDLE_0_OVERRIDE": 2.0,
            "MIN_SPINDLE_0_SPEED": 0,
            "MAX_SPINDLE_0_SPEED": 22000,
            "DEFAULT_SPINDLE_0_SPEED": 6000,
            "SPINDLE_INCREMENT": 100,
            "MAX_SPINDLE_POWER": 1500,
        },
        "MQTT": {
            # "DRYRUN": "--dryrun",
            "DRYRUN": "",
            "BROKER": "localhost",
            "USERNAME": "",
            "PASSWORD": "",
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
            "SPINDLES": 1,
        },
        "EMCIO": {
            "EMCIO": "io",
            "CYCLE_TIME": 0.100,
            "TOOL_TABLE": "tool.tbl",
        },
    }
    SHORTENER = {
        "input": "in",
        "output": "out",
        "spindle": "spl",
        "lower": "lo",
        "limit": "lim",
        "encoder": "enc",
        "enable": "en",
        "duty": "sty",
        "count": "cnt",
        "feedback": "fb",
        "position": "pos",
        "velocity": "vel",
        "index": "idx",
        "pwmgen": "pwm",
        "stepgen": "sg",
        "gpio": "io",
    }

    def __init__(self, project):
        self.postgui_call_rm = []
        self.postgui_call_list = []
        self.pregui_call_list = []
        self.feedbacks = []
        self.halextras = []
        self.mqtt_publisher = []
        self.project = project
        self.protocol = self.project.config["jdata"].get("protocol", "SPI")
        self.base_path = os.path.join(self.project.config["output_path"], "LinuxCNC")
        self.component_path = f"{self.base_path}"
        self.configuration_path = f"{self.base_path}"

        # expand JOINT_DEFAULTS
        for plugin_instance in self.project.plugin_instances:
            if plugin_instance.JOINT_DEFAULTS:
                self.JOINT_DEFAULTS.update(plugin_instance.JOINT_DEFAULTS)

        # update_prefixes for multiple used components
        components = {}
        for plugin_instance in self.project.plugin_instances:
            if plugin_instance.COMPONENT:
                if plugin_instance.COMPONENT not in components:
                    components[plugin_instance.COMPONENT] = []
                components[plugin_instance.COMPONENT].append(plugin_instance)
        for component_type, instances in components.items():
            # run update_prefixes on the first instance of the plugin if exist
            if hasattr(instances[0], "update_prefixes"):
                instances[0].update_prefixes(self, instances)
            elif instances[0].TYPE == "base":
                # base plugins by instance name
                for instance in instances:
                    instance.PREFIX = f"{component_type}.{instance.instances_name}"
            else:
                # io plugins by instance idx
                for num, instance in enumerate(instances):
                    instance.PREFIX = f"{component_type}.{num}"

        machinetype = self.project.config["jdata"].get("linuxcnc", {}).get("machinetype")
        self.project.axis_names = "XYZACBUVW"
        if machinetype in {"melfa", "melfa_nogl", "puma"}:
            self.project.axis_names = "XYZABC"

        self.project.axis_dict = self.create_axis_config(self.project)
        num_joints = 0
        for _axis, values in self.project.axis_dict.items():
            num_joints += len(values["joints"])
        self.num_joints = num_joints

        self.addons = {}
        self.gpionames = []
        for addon_path in glob.glob(os.path.join(riocore_path, "generator", "addons", "*", "linuxcnc.py")):
            addon_name = addon_path.split(os.sep)[-2]
            self.addons[addon_name] = importlib.import_module(".linuxcnc", f"riocore.generator.addons.{addon_name}")

    def cfglink(self):
        try:
            jdata = self.project.config["jdata"]
            name = jdata.get("name")
            source = os.path.realpath(self.component_path)
            target_dir = os.path.join(os.path.expanduser("~"), "linuxcnc", "configs")
            target_file = os.path.join(target_dir, name)
            if os.path.islink(target_file):
                os.unlink(target_file)
            os.makedirs(target_dir, exist_ok=True)
            os.symlink(source, target_file)
        except Exception as error:
            riocore.log(f"ERROR(cgflink): {error}")

    def readme(self):
        os.makedirs(self.component_path, exist_ok=True)
        target = os.path.join(self.component_path, "README")
        open(target, "w").write(self.project.info())

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

        for plugin_instance in self.project.plugin_instances:
            if hasattr(plugin_instance, "start_sh"):
                output.append(f"### {plugin_instance.NAME} ({plugin_instance.instances_name}) ###")
                output.append(plugin_instance.start_sh(self))

        if self.gui_type == "qtvcp":
            # we need sudo to copy the vcp stuff to qtvcp-panels
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

    def generator(self, preview=False):
        self.preview = preview
        jdata = self.project.config["jdata"]
        linuxcnc_config = jdata.get("linuxcnc", {})
        gui = linuxcnc_config.get("gui", "axis")
        vcp_mode = linuxcnc_config.get("vcp_mode", "ALL")
        vcp_type = linuxcnc_config.get("vcp_type", "auto")

        self.gui_type = ""
        self.gui_prefix = ""
        self.gui_tablocation = ""
        if vcp_mode != "NONE":
            if gui == "axis":
                if vcp_type == "gladevcp":
                    self.gui_type = "gladevcp"
                    self.gui_prefix = "gladevcp"
                else:
                    self.gui_type = "pyvcp"
                    self.gui_prefix = "pyvcp"
            elif gui == "gmoccapy":
                self.gui_type = "gladevcp"
                self.gui_prefix = "rio-gui"
                self.gui_tablocation = "ntb_user_tabs"
            elif gui in {"qtdragon", "qtdragon_hd"}:
                self.gui_type = "qtvcp"
                self.gui_prefix = "qtdragon.rio-gui"
            elif gui in {"probe_basic", "probe_basic_lathe"}:
                self.gui_type = "qtpyvcp"
                self.gui_prefix = "qtpyvcp"
            elif gui in {"gscreen"}:
                self.gui_type = "gladevcp"
                self.gui_prefix = "rio-gui"
                self.gui_tablocation = "notebook_main"
            elif gui in {"flexgui"}:
                self.gui_type = "flexvcp"
                self.gui_prefix = "flexhal.rio"
            elif gui in {"tnc"}:
                self.gui_type = "qtpyvcp"
                self.gui_prefix = "qtpyvcp"
            # elif gui in {"woodpecker"}:
            #    self.gui_type = "qtvcp"
            #    self.gui_prefix = "qtvcp"

        if not self.preview:
            self.cfglink()
        self.startscript()
        self.readme()
        self.hal()
        self.riof()
        self.misc()
        for addon_name, addon in self.addons.items():
            if hasattr(addon, "generator"):
                addon.generator(self)
        self.ini()
        os.makedirs(self.configuration_path, exist_ok=True)

        # add user defined networks
        for pin_from, pin_to in linuxcnc_config.get("halsignals", {}).items():
            self.halg.net_add(pin_from, pin_to)

        output_hal = []
        output_postgui = []
        (network_hal, network_postgui) = self.halg.net_write()
        output_hal += network_hal
        output_postgui += network_postgui
        output_postgui += [""]
        output_hal += self.halextras

        output_hal.append("")
        open(os.path.join(self.configuration_path, "rio.hal"), "w").write("\n".join(output_hal))
        open(os.path.join(self.configuration_path, "custom_postgui.hal"), "w").write("\n".join(output_postgui))

        if (gui == "gmoccapy" or gui == "gscreen") and self.gui_type == "gladevcp":
            riocore.log("## INFO: custom_postgui.hal will be load by gladevcp")
            self.postgui_call_rm.append("custom_postgui.hal")
        else:
            self.postgui_call_list.append("custom_postgui.hal")

        list_data = []
        if os.path.isfile(os.path.join(self.configuration_path, "postgui_call_list.hal")):
            # read existing file to keep custom entry's
            cl_data = open(os.path.join(self.configuration_path, "postgui_call_list.hal")).read()
            for line in cl_data.split("\n"):
                if line.startswith("source "):
                    source = line.split()[1]
                    if source in self.postgui_call_rm:
                        continue
                    if source in self.postgui_call_list:
                        self.postgui_call_list.remove(source)
                list_data.append(line.strip())

        for halfile in self.postgui_call_list:
            list_data.append(f"source {halfile}")
        open(os.path.join(self.configuration_path, "postgui_call_list.hal"), "w").write("\n".join(list_data))

        extra_data = []
        if os.path.isfile(os.path.join(self.configuration_path, "pregui_call_list.hal")):
            # read existing file to keep custom entry's
            cl_data = open(os.path.join(self.configuration_path, "pregui_call_list.hal")).read()
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

        riocore.log(f"writing linuxcnc files to: {self.base_path}")

        syncto = self.project.config["jdata"].get("syncto")
        if syncto:
            syc_cmd = f"rsync -avr {self.project.config['output_path']}/ {syncto}"
            riocore.log(f"INFO: {syc_cmd}")
            os.system(syc_cmd)

    def ini_mdi_command(self, command, title=None):
        """Used by addons to add mdi-command's and prevent doubles"""
        jdata = self.project.config["jdata"]
        ini = self.ini_defaults(jdata, num_joints=5, axis_dict=self.project.axis_dict, gui_type=self.gui_type)
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
        vcp_pos = linuxcnc_config.get("vcp_pos", "RIGHT")
        machinetype = linuxcnc_config.get("machinetype")
        embed_vismach = linuxcnc_config.get("embed_vismach")

        netlist = []
        for plugin in jdata.get("plugins", []):
            for signal in plugin.get("signals", {}).values():
                if net := signal.get("net"):
                    netlist.append(net)

        if machinetype:
            ini_setup["EMC"]["MACHINE"] = f"Rio - {machinetype}"

        if machinetype == "lathe":
            ini_setup["DISPLAY"]["LATHE"] = 1

        coordinates = []
        for axis_name, axis_config in axis_dict.items():
            for joint_setup in axis_config["joints"]:
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
        elif machinetype in {"melfa", "melfa_nogl"}:
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
            ini_setup["HALUI"][f"MDI_COMMAND||Zero|{axis_name}"] = f"G92 {axis_name}0"
            if "motion.probe-input" in netlist:
                if machinetype == "lathe":
                    if axis_name == "X":
                        ini_setup["HALUI"]["MDI_COMMAND||Touch|Touch-X"] = "o<x_touch> call"
                    elif axis_name == "Z":
                        ini_setup["HALUI"]["MDI_COMMAND||Touch|Touch-Z"] = "o<z_touch> call"
                elif axis_name == "Z":
                    ini_setup["HALUI"]["MDI_COMMAND||Touch|Touch-Z"] = "o<z_touch> call"

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
            if gui_type == "gladevcp":
                if vcp_pos == "TAB":
                    ini_setup["DISPLAY"]["EMBED_TAB_LOCATION|PYVCP"] = "ntb_user_tabs"
                else:
                    ini_setup["DISPLAY"]["EMBED_TAB_LOCATION|PYVCP"] = "box_right"
                ini_setup["DISPLAY"]["EMBED_TAB_NAME|PYVCP"] = "RIO"
                ini_setup["DISPLAY"]["EMBED_TAB_COMMAND|PYVCP"] = "gladevcp -x {XID} -H custom_postgui.hal rio-gui.ui"

        elif gui == "gscreen":
            ini_setup["DISPLAY"]["DISPLAY"] = gui
            ini_setup["DISPLAY"]["CYCLE_TIME"] = "150"
            ini_setup["DISPLAY"]["EMBED_TAB_NAME|PYVCP"] = "RIO"
            ini_setup["DISPLAY"]["EMBED_TAB_LOCATION|PYVCP"] = "notebook_main"
            ini_setup["DISPLAY"]["EMBED_TAB_COMMAND|PYVCP"] = "gladevcp -x {XID} -H custom_postgui.hal rio-gui.ui"
            ini_setup["TOOLSENSOR"] = {
                "MAXPROBE": "-10",
                "SENSOR_HEIGHT": "25.0",
                "SEARCH_VEL": "60",
                "PROBE_VEL": "30",
                "X": "10.0",
                "Y": "10.0",
                "Z": "-80.0",
            }
            for axis_name, axis_config in axis_dict.items():
                if axis_name not in {"X", "Y", "Z"}:
                    ini_setup["TOOLSENSOR"][axis_name] = "0.0"

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

        elif gui in {"woodpecker"}:
            ini_setup["DISPLAY"]["DISPLAY"] = "qtvcp woodpecker"
            # ini_setup["DISPLAY"]["EMBED_TAB_NAME|RIO"] = "RIO"
            # ini_setup["DISPLAY"]["EMBED_TAB_LOCATION|RIO"] = "main_tab_widget"
            # ini_setup["DISPLAY"]["EMBED_TAB_COMMAND|RIO"] = "qtvcp rio-gui"

        elif gui in {"flexgui"}:
            ini_setup["DISPLAY"]["DISPLAY"] = "flexgui"
            ini_setup["DISPLAY"]["TOOL_EDITOR"] = "tooledit"
            ini_setup["DISPLAY"]["EMBED_TAB_NAME|RIO"] = "RIO"
            ini_setup["FLEXGUI"] = {
                "QSS": "flexgui.qss",
            }

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

            if "motion.probe-input" in netlist:
                qtdragon_setup["PROBE"]["USE_PROBE"] = "versaprobe"

            if gui_type == "qtvcp":
                qtdragon_setup["DISPLAY"]["EMBED_TAB_NAME|RIO"] = "RIO"
                qtdragon_setup["DISPLAY"]["EMBED_TAB_COMMAND|RIO"] = "qtvcp rio-gui"
                # qtdragon_setup["DISPLAY"]["EMBED_TAB_LOCATION|RIO"] = "tabWidget_utilities"
                qtdragon_setup["DISPLAY"]["EMBED_TAB_LOCATION|RIO"] = "stackedWidget_mainTab"

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
        dios = self.halg.get_dios()
        aios = self.halg.get_aios()

        if dios > 64:
            riocore.log("ERROR: you can only configure up to 64 motion.digital-in-NN/motion.digital-out-NN")
        if aios > 64:
            riocore.log("ERROR: you can only configure up to 64 motion.analog-in-NN/motion.analog-out-NN")

        ini_setup = self.ini_defaults(self.project.config["jdata"], num_joints=self.num_joints, axis_dict=self.project.axis_dict, dios=dios, aios=aios, gui_type=self.gui_type)

        if not self.mqtt_publisher:
            del ini_setup["MQTT"]

        self.vcp_gui()

        for section, section_options in linuxcnc_config.get("ini", {}).items():
            if section not in ini_setup:
                ini_setup[section] = {}
            for key, value in section_options.items():
                ini_setup[section][key] = value

        for addon_name, addon in self.addons.items():
            if hasattr(addon, "ini"):
                addon.ini(self, ini_setup)

        for plugin_instance in self.project.plugin_instances:
            if hasattr(plugin_instance, "ini"):
                plugin_instance.ini(self, ini_setup)

        # update VELOCITY values
        max_linear_velocity = 0
        max_angular_velocity = 0
        for axis_name, axis_config in self.project.axis_dict.items():
            for joint_setup in axis_config["joints"]:
                if joint_setup["TYPE"] == "LINEAR":
                    max_linear_velocity = max(max_linear_velocity, joint_setup["MAX_VELOCITY"])
                else:
                    max_angular_velocity = max(max_angular_velocity, joint_setup["MAX_VELOCITY"])
        max_linear_velocity = min(max_linear_velocity, ini_setup["DISPLAY"]["MAX_LINEAR_VELOCITY"]) or ini_setup["DISPLAY"]["MAX_LINEAR_VELOCITY"]
        default_linear_velocity = min(max_linear_velocity, ini_setup["DISPLAY"]["DEFAULT_LINEAR_VELOCITY"], ini_setup["TRAJ"]["DEFAULT_LINEAR_VELOCITY"]) or ini_setup["DISPLAY"]["DEFAULT_LINEAR_VELOCITY"]
        ini_setup["DISPLAY"]["MAX_LINEAR_VELOCITY"] = max_linear_velocity
        ini_setup["TRAJ"]["MAX_LINEAR_VELOCITY"] = max_linear_velocity
        ini_setup["DISPLAY"]["DEFAULT_LINEAR_VELOCITY"] = default_linear_velocity
        ini_setup["TRAJ"]["DEFAULT_LINEAR_VELOCITY"] = default_linear_velocity
        max_angular_velocity = min(max_angular_velocity, ini_setup["DISPLAY"]["MAX_ANGULAR_VELOCITY"]) or ini_setup["DISPLAY"]["MAX_ANGULAR_VELOCITY"]
        default_angular_velocity = min(max_angular_velocity, ini_setup["DISPLAY"]["DEFAULT_ANGULAR_VELOCITY"], ini_setup["TRAJ"]["DEFAULT_ANGULAR_VELOCITY"]) or ini_setup["DISPLAY"]["DEFAULT_ANGULAR_VELOCITY"]
        ini_setup["DISPLAY"]["MAX_ANGULAR_VELOCITY"] = max_angular_velocity
        ini_setup["TRAJ"]["MAX_ANGULAR_VELOCITY"] = max_angular_velocity
        ini_setup["DISPLAY"]["DEFAULT_ANGULAR_VELOCITY"] = default_angular_velocity
        ini_setup["TRAJ"]["DEFAULT_ANGULAR_VELOCITY"] = default_angular_velocity

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

        for axis_name, axis_config in self.project.axis_dict.items():
            output.append(f"[AXIS_{axis_name}]")
            axis_setup = copy.deepcopy(self.AXIS_DEFAULTS)
            axis_max_velocity = 10000.0
            axis_max_acceleration = 10000.0
            axis_min_limit = 100000.0
            axis_max_limit = -100000.0
            axis_backlash = 0.0
            axis_ferror = axis_setup["FERROR"]
            for joint_setup in axis_config["joints"]:
                joint = joint_setup["num"]
                max_velocity = joint_setup["MAX_VELOCITY"]
                max_acceleration = joint_setup["MAX_ACCELERATION"]
                min_limit = joint_setup["MIN_LIMIT"]
                max_limit = joint_setup["MAX_LIMIT"]
                backlash = joint_setup.get("BACKLASH", 0.0)
                ferror = joint_setup.get("FERROR", axis_ferror)
                axis_max_velocity = min(axis_max_velocity, max_velocity)
                axis_max_acceleration = min(axis_max_acceleration, max_acceleration)
                axis_min_limit = min(axis_min_limit, min_limit)
                axis_max_limit = max(axis_max_limit, max_limit)

                axis_backlash = max(axis_backlash, backlash)
                axis_ferror = max(axis_ferror, ferror)

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

            for joint_config in axis_config["joints"]:
                joint = joint_config["num"]
                position_mode = joint_config.get("mode", "velocity")
                plugin_instance = joint_config["instance"]
                output.append(f"[JOINT_{joint}]")
                output.append(f"# {plugin_instance.instances_name}")
                if position_mode == "velocity":
                    pid_setup = self.PID_DEFAULTS.copy()
                    for key, value in pid_setup.items():
                        setup_value = joint_config.get(f"PID_{key.upper()}")
                        if setup_value:
                            value = setup_value
                        output.append(f"{key:18s} = {value}")
                    output.append("")

                options = [
                    "TYPE",
                    "FERROR",
                    "MIN_LIMIT",
                    "MAX_LIMIT",
                    "MAX_VELOCITY",
                    "MAX_ACCELERATION",
                    "SCALE_OUT",
                    "SCALE_IN",
                    "HOME_SEARCH_VEL",
                    "HOME_LATCH_VEL",
                    "HOME_FINAL_VEL",
                    "HOME_IGNORE_LIMITS",
                    "HOME_USE_INDEX",
                    "HOME_OFFSET",
                    "HOME",
                    "HOME_SEQUENCE",
                ] + plugin_instance.JOINT_OPTIONS
                for key, value in joint_config.items():
                    if key in options:
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
                            self.halg.setp_add(f"{halname}-scale", scale)
                        if offset:
                            self.halg.setp_add(f"{halname}-offset", offset)

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
                    elif function and rio_function[0] in {"chargepump"}:
                        if rio_function[0] not in self.rio_functions:
                            self.rio_functions[rio_function[0]] = []
                        self.rio_functions[rio_function[0]].append(halname)
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

        if "chargepump" in self.rio_functions:
            outputs = self.rio_functions["chargepump"]
            self.halg.fmt_add_top("# charge_pump / watchdog output")
            self.halg.fmt_add_top("loadrt charge_pump")
            self.halg.fmt_add_top("")
            self.halg.fmt_add_top("addf charge-pump servo-thread")
            for output in outputs:
                self.halg.net_add("charge-pump.out-4", output)

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
                    self.halg.net_add(source, f"riof.{source}.in")

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
                elif function in {"fast"} or function in {"speed0"} or function in {"speed1"}:
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
                    if function == "speed0" or function == "speed1" or function == "fast":
                        speed_selector_mux *= 2

                # TODO: using mux-gen ?
                if speed_selector_mux > 4:
                    riocore.log("ERROR: only two speed selectors are supported")
                    speed_selector_mux = 4
                elif speed_selector_mux == 1:
                    riocore.log("ERROR: no speed selectors found")

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
                                self.halg.net_add(halname, "riof.jog.wheelscale_mux.sel")
                            else:
                                self.halg.net_add(halname, f"riof.jog.wheelscale_mux.sel{in_n}")
                                in_n += 1

                    # pname = gui_gen.draw_number("Jogscale", "jogscale")
                    # self.halg.net_add("riof.jog.wheelscale_mux.out", pname)

            if wheel:
                halname_wheel = ""
                for function, halname in self.rio_functions["jog"].items():
                    if function == "wheel":
                        halname_wheel = f"{halname}-s32"
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
                    for axis_name, axis_config in self.project.axis_dict.items():
                        laxis = axis_name.lower()
                        self.halg.setp_add(f"axis.{laxis}.jog-vel-mode", 1)

                        if wheel_scale is not None:
                            self.halg.setp_add(f"axis.{laxis}.jog-scale", wheel_scale)
                        else:
                            self.halg.net_add("riof.jog.wheelscale_mux.out", f"axis.{laxis}.jog-scale")

                        if gui == "axis":
                            self.halg.net_add(f"axisui.jog.{laxis}", f"axis.{laxis}.jog-enable", f"jog-{laxis}-enable")
                            self.halg.net_add(halname_wheel, f"axis.{laxis}.jog-counts", f"jog-{laxis}-counts")
                            for joint_setup in axis_config["joints"]:
                                joint = joint_setup["num"]
                                self.halg.setp_add(f"joint.{joint}.jog-vel-mode", 1)

                                if wheel_scale is not None:
                                    self.halg.setp_add(f"joint.{joint}.jog-scale", wheel_scale)
                                else:
                                    self.halg.net_add("riof.jog.wheelscale_mux.out", f"joint.{joint}.jog-scale")

                                self.halg.net_add(f"axisui.jog.{laxis}", f"joint.{joint}.jog-enable", f"jog-{joint}-enable")
                                self.halg.net_add(halname_wheel, f"joint.{joint}.jog-counts", f"jog-{joint}-counts")

            else:
                for axis_name, axis_config in self.project.axis_dict.items():
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
                                self.halg.net_add(f"{halname}-s32", f"axis.{laxis}.jog-counts", f"jog-{laxis}-counts")

                        for joint_setup in axis_config["joints"]:
                            joint = joint_setup["num"]
                            self.halg.setp_add(f"joint.{joint}.jog-vel-mode", 1)

                            if wheel_scale is not None:
                                self.halg.setp_add(f"joint.{joint}.jog-scale", wheel_scale)
                            else:
                                self.halg.net_add("riof.jog.wheelscale_mux.out", f"joint.{joint}.jog-scale")

                            self.halg.setp_add(f"joint.{joint}.jog-enable", 1)
                            for function, halname in self.rio_functions["jog"].items():
                                if function == fname:
                                    self.halg.net_add(f"{halname}-s32", f"joint.{joint}.jog-counts", f"jog-{joint}-counts")

            if speed_selector:
                speed_selector_mux = 1

                for function, halname in self.rio_functions["jog"].items():
                    if function == "speed0" or function == "speed1" or function == "fast":
                        speed_selector_mux *= 2

                if speed_selector_mux > 4:
                    riocore.log("ERROR: only two speed selectors are supported")
                    speed_selector_mux = 4
                elif speed_selector_mux == 1:
                    riocore.log("ERROR: no speed selectors found")

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
                                self.halg.net_add(f"{halname}", "riof.jog.speed_mux.sel")
                            else:
                                self.halg.net_add(f"{halname}", f"riof.jog.speed_mux.sel{in_n}")
                                in_n += 1

                    # pname = gui_gen.draw_number("Jogspeed", "jogspeed")
                    # self.halg.net_add("riof.jog.speed_mux.out", pname)
                    self.halg.net_add("riof.jog.speed_mux.out", "halui.axis.jog-speed")
                    self.halg.net_add("riof.jog.speed_mux.out", "halui.joint.jog-speed")
            else:
                self.halg.setp_add("halui.axis.jog-speed", riof_jog_setup("keys", "speed"))
                self.halg.setp_add("halui.joint.jog-speed", riof_jog_setup("keys", "speed"))

            if axis_move:
                for function, halname in self.rio_functions["jog"].items():
                    if function in {"plus", "minus"}:
                        self.halg.net_add(f"{halname}", f"halui.joint.selected.{function}")
                        self.halg.net_add(f"{halname}", f"halui.axis.selected.{function}")

            if axis_selector:
                joint_n = 0
                for function, halname in self.rio_functions["jog"].items():
                    if function.startswith("select-"):
                        axis_name = function.split("-")[-1]
                        self.halg.net_add(f"{halname}", f"halui.axis.{axis_name}.select")
                        self.halg.net_add(f"{halname}", f"halui.joint.{joint_n}.select")
                        # pname = gui_gen.draw_led(f"Jog:{axis_name}", f"selected-{axis_name}")
                        # self.halg.net_add(f"halui.axis.{axis_name}.is-selected", pname)
                        for axis_id, axis_config in self.project.axis_dict.items():
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
                                    for joint_setup in axis_config["joints"]:
                                        joint = joint_setup["num"]
                                        self.halg.net_add(f"riof.axisui-{laxis}-oneshot.out", f"halui.joint.{joint}.select")
                        joint_n += 1
            else:
                for axis_id, axis_config in self.project.axis_dict.items():
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
                        for joint_setup in axis_config["joints"]:
                            joint = joint_setup["num"]
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
                        self.halg.net_add("riof.jog.position_mux.out-f", f"{halname}")

            if axis_leds:
                for function, halname in self.rio_functions["jog"].items():
                    if function.startswith("selected-"):
                        axis_name = function.split("-")[-1]
                        self.halg.net_add(f"halui.axis.{axis_name}.is-selected", f"{halname}")

    def vcp_gui(self):
        os.makedirs(self.configuration_path, exist_ok=True)
        linuxcnc_config = self.project.config["jdata"].get("linuxcnc", {})
        json_path = self.project.config["json_path"]
        gui = linuxcnc_config.get("gui", "axis")
        machinetype = linuxcnc_config.get("machinetype")
        embed_vismach = linuxcnc_config.get("embed_vismach")
        vcp_sections = linuxcnc_config.get("vcp_sections", [])
        vcp_mode = linuxcnc_config.get("vcp_mode", "ALL")
        vcp_pos = linuxcnc_config.get("vcp_pos", "RIGHT")
        ini_setup = self.ini_defaults(self.project.config["jdata"], num_joints=self.num_joints, axis_dict=self.project.axis_dict, gui_type=self.gui_type)

        if gui in {"flexgui"}:
            os.makedirs(os.path.join(self.configuration_path), exist_ok=True)
            ini_setup["DISPLAY"]["DISPLAY"] = "./flexgui"
            ini_setup["DISPLAY"]["GUI"] = "flexgui.ui"
            ini_setup["FLEXGUI"] = {}
            ini_setup["FLEXGUI"]["QSS"] = "flexgui.qss"
            flexgui = linuxcnc_config.get("flexgui", "axis")
            if flexgui:
                for source in glob.glob(os.path.join(riocore_path, "gui", "flexgui", "guis", flexgui, "*")):
                    target_path = os.path.join(self.configuration_path, os.path.basename(source))
                    if os.path.isfile(source):
                        shutil.copy(source, target_path)
                    else:
                        shutil.copytree(source, target_path, dirs_exist_ok=True)

            for uifile in glob.glob(os.path.join(json_path, "flexgui.ui")):
                target_path = os.path.join(self.configuration_path, os.path.basename(uifile))
                shutil.copy(uifile, target_path)

            for source in glob.glob(os.path.join(riocore_path, "gui", "flexgui", "*")):
                if source.endswith("/guis"):
                    continue
                target_path = os.path.join(self.configuration_path, os.path.basename(source))
                if os.path.isfile(source):
                    shutil.copy(source, target_path)
                else:
                    shutil.copytree(source, target_path, dirs_exist_ok=True)
                if target_path.endswith("/flexgui"):
                    os.chmod(target_path, stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR | stat.S_IRGRP | stat.S_IXGRP | stat.S_IROTH | stat.S_IXOTH)

            for qssfile in glob.glob(os.path.join(json_path, "flexgui.qss")):
                target_path = os.path.join(self.configuration_path, os.path.basename(qssfile))
                shutil.copy(qssfile, target_path)
            for pyfile in glob.glob(os.path.join(json_path, "flexgui.py")):
                target_path = os.path.join(self.configuration_path, os.path.basename(pyfile))
                ini_setup["FLEXGUI"]["RESOURCES"] = "flexgui.py"
                shutil.copy(pyfile, target_path)
            for pyfile in glob.glob(os.path.join(json_path, "flexgui")):
                target_path = os.path.join(self.configuration_path, os.path.basename(pyfile))
                shutil.copy(pyfile, target_path)
            for pyfile in glob.glob(os.path.join(json_path, "libflexgui")):
                target_path = os.path.join(self.configuration_path, os.path.basename(pyfile))
                shutil.copytree(pyfile, target_path, dirs_exist_ok=True)
            for pyfile in glob.glob(os.path.join(json_path, "flexgui-images")):
                target_path = os.path.join(self.configuration_path, os.path.basename(pyfile))
                shutil.copytree(pyfile, target_path, dirs_exist_ok=True)

        elif gui in {"tnc"}:
            try:
                import tnc

                tnc_path = os.path.dirname(tnc.__file__)
                os.makedirs(os.path.join(self.configuration_path), exist_ok=True)
                ini_setup["DISPLAY"]["DISPLAY"] = "./tnc"
                for part in ("ui", "style.qss", "dialogs", "config.yml"):
                    for source in glob.glob(os.path.join(tnc_path, part)):
                        target_path = os.path.join(self.configuration_path, os.path.basename(source))
                        if os.path.isfile(source):
                            shutil.copy(source, target_path)
                        else:
                            shutil.copytree(source, target_path, dirs_exist_ok=True)

                tnc_main = r"""#!/usr/bin/python3
# -*- coding: utf-8 -*-
import os
import re
import sys
from tnc import main
from qtpyvcp.utilities.opt_parser import parse_opts

VCP_DIR = os.path.realpath(os.path.dirname(__file__))
VCP_CONFIG_FILE = os.path.join(VCP_DIR, "config.yml")

if __name__ == "__main__":
    sys.argv[0] = re.sub(r"(-script\.pyw|\.exe)?$", "", sys.argv[0])
    opts = parse_opts(vcp_cmd="tnc", vcp_name="TurBoNC", vcp_version="0.1.rio")

    # opts["fullscreen"] = True
    # opts["confirm_exit"] = False
    opts["config_file"] = VCP_CONFIG_FILE

    sys.exit(main(opts))
"""
                target_path = os.path.join(self.configuration_path, "tnc")
                open(target_path, "w").write(tnc_main)
                os.chmod(target_path, stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR | stat.S_IRGRP | stat.S_IXGRP | stat.S_IROTH | stat.S_IXOTH)
                shutil.copy(os.path.join(tnc_path, "ui", "window.ui"), os.path.join(self.configuration_path, "ui", "window.ui"))
            except Exception:
                riocore.log("ERROR: no tnc installation found")

        gui_gen = None
        if vcp_mode != "NONE":
            if self.gui_type == "gladevcp":
                gui_gen = gladevcp(self.gui_prefix, vcp_pos=vcp_pos)
            elif self.gui_type == "pyvcp":
                gui_gen = pyvcp(self.gui_prefix, vcp_pos=vcp_pos)
            elif self.gui_type == "gladevcp":
                gui_gen = gladevcp(self.gui_prefix, vcp_pos=vcp_pos)
            elif self.gui_type == "qtvcp":
                if gui in {"woodpecker"}:
                    vcp_pos = "TAB"
                gui_gen = qtvcp(self.gui_prefix, vcp_pos=vcp_pos)
            elif self.gui_type == "qtpyvcp":
                gui_gen = qtpyvcp(self.gui_prefix, vcp_pos=vcp_pos, mode=gui)
            elif self.gui_type == "flexvcp":
                gui_gen = flexvcp(self.gui_prefix, vcp_pos=vcp_pos)

        if not gui_gen:
            return

        if not gui_gen.check(self.configuration_path):
            riocore.log("ERROR: vcp: vcp-gui is disabled")
            return

        gui_gen.draw_begin()

        # build complete list of sections (in right order)
        for section in ("status", "inputs", "outputs", "virtual"):
            if section not in vcp_sections:
                vcp_sections.append(section)
        for plugin_instance in self.project.plugin_instances:
            for signal_name, signal_config in plugin_instance.signals().items():
                if plugin_instance.plugin_setup.get("is_joint", False) and signal_name in {"position", "velocity", "position-cmd", "enable", "dty"}:
                    continue
                userconfig = signal_config.get("userconfig", {})
                displayconfig = userconfig.get("display", signal_config.get("display", {}))
                section = displayconfig.get("section", "").lower()
                if section and section not in vcp_sections:
                    vcp_sections.append(section)

        # analyse halnames to generate titles
        prefixes = {}
        haltitles = {}
        for plugin_instance in self.project.plugin_instances:
            for signal_name, signal_config in plugin_instance.signals().items():
                if plugin_instance.plugin_setup.get("is_joint", False) and signal_name in {"position", "velocity", "position-cmd", "enable", "dty"}:
                    continue
                halname = signal_config["halname"]
                prefix = ".".join(halname.split(".")[:-1])
                if prefix not in prefixes:
                    prefixes[prefix] = []
                prefixes[prefix].append(halname)
        for prefix, halnames in prefixes.items():
            if len(halnames) == 1:
                for halname in halnames:
                    haltitles[halname] = prefix.title()

        def vcp_add(signal_config, widgets, errors=False):
            halname = signal_config["halname"]
            netname = signal_config["netname"]
            direction = signal_config["direction"]
            userconfig = signal_config.get("userconfig", {})
            boolean = signal_config.get("bool")
            u32 = signal_config.get("u32")
            s32 = signal_config.get("s32")
            virtual = signal_config.get("virtual")
            mapping = signal_config.get("mapping")
            setp = userconfig.get("setp")
            function = userconfig.get("function", "")
            displayconfig = userconfig.get("display", signal_config.get("display", {}))
            initval = signal_config.get("default", 0)
            if not displayconfig and initval:
                displayconfig["initval"] = initval
            if not displayconfig.get("title"):
                displayconfig["title"] = f"{plugin_instance.title}-{signal_name}"
            if vcp_mode == "CONFIGURED" and not displayconfig.get("type") and not displayconfig.get("title"):
                return
            if function and not virtual:
                return
            if signal_config.get("helper", False) and not displayconfig:
                return
            if setp:
                return
            if halname in self.feedbacks:
                return

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

            dtype = None
            section = None
            group = displayconfig.get("group", None)

            if direction == "input" and netname and "iocontrol.0.emc-enable-in" in netname:
                section = displayconfig.get("section", "status").lower()
                group = "ESTOP-STATUS"
                if "type" in displayconfig:
                    dtype = displayconfig["type"]
                else:
                    dtype = "rectled"
                    if netname[0] == "!":
                        displayconfig["color"] = "red"
                        displayconfig["off_color"] = "green"
                    else:
                        displayconfig["color"] = "green"
                        displayconfig["off_color"] = "red"

            elif direction == "input" and netname and "motion.enable" in netname:
                section = displayconfig.get("section", "status").lower()
                group = "MACHINE-STATUS"
                if "type" in displayconfig:
                    dtype = displayconfig["type"]
                else:
                    dtype = "rectled"
                    if netname[0] == "!":
                        displayconfig["color"] = "red"
                        displayconfig["off_color"] = "green"
                    else:
                        displayconfig["color"] = "green"
                        displayconfig["off_color"] = "red"

            elif (netname and not virtual) or setp:
                if direction == "input":
                    section = displayconfig.get("section", "inputs").lower()
                elif direction == "output":
                    section = displayconfig.get("section", "outputs").lower()
                if boolean:
                    dtype = displayconfig.get("type", "led")
                elif u32:
                    dtype = displayconfig.get("type", "number_u32")
                elif s32:
                    dtype = displayconfig.get("type", "number_s32")
                else:
                    dtype = displayconfig.get("type", "number")

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
                if mapping and hasattr(gui_gen, "draw_multilabel"):
                    dtype = displayconfig.get("type", "multilabel")
                elif boolean:
                    dtype = displayconfig.get("type", "led")
                elif u32:
                    dtype = displayconfig.get("type", "number_u32")
                elif s32:
                    dtype = displayconfig.get("type", "number_s32")
                else:
                    dtype = displayconfig.get("type", "number")
            elif direction == "output":
                section = displayconfig.get("section", "outputs").lower()
                if boolean:
                    dtype = displayconfig.get("type", "checkbutton")
                elif u32:
                    dtype = displayconfig.get("type", "scale_u32")
                elif s32:
                    dtype = displayconfig.get("type", "scale_s32")
                else:
                    dtype = displayconfig.get("type", "scale")
            if hasattr(gui_gen, f"draw_{dtype}"):
                if section not in widgets:
                    widgets[section] = {}
                if group not in widgets[section]:
                    widgets[section][group] = []
                widgets[section][group].append(
                    {
                        "section": section,
                        "group": group,
                        "direction": direction,
                        "boolean": boolean,
                        "virtual": virtual,
                        "halname": halname,
                        "netname": netname,
                        "mapping": mapping,
                        "setp": setp,
                        "dtype": dtype,
                        "displayconfig": displayconfig,
                    }
                )
            elif dtype not in {"none", "None", None}:
                riocore.log(f"WARNING: 'draw_{dtype}' not found")

        widgets = {}
        for plugin_instance in self.project.plugin_instances:
            for signal_name, signal_config in plugin_instance.signals().items():
                if plugin_instance.plugin_setup.get("is_joint", False) and signal_name in {"position", "position-scale", "position-fb", "velocity", "position-cmd", "enable", "dty"}:
                    continue
                vcp_add(signal_config, widgets)

        tablist = []
        for tab in vcp_sections:
            if tab not in widgets and tab != "status":
                continue
            tablist.append(tab)
        gui_gen.draw_tabs_begin([tab.title() for tab in tablist])

        # generate tab (vcp) for each section
        for tab in tablist:
            gui_gen.draw_tab_begin(tab.title())

            if tab == "status":
                if machinetype in {"melfa", "melfa_nogl"}:
                    if hasattr(gui_gen, "draw_multilabel"):
                        pname = gui_gen.draw_multilabel("kinstype", "kinstype", setup={"legends": ["WORLD COORD", "JOINT COORD"]})
                        self.halg.net_add("kinstype.is-0", f"{pname}.legend0")
                        self.halg.net_add("kinstype.is-1", f"{pname}.legend1")
                    pname = gui_gen.draw_button("Clear Path", "vismach-clear")

                    gui_gen.draw_hbox_begin()

                    if embed_vismach:
                        self.halg.net_add(pname, f"{embed_vismach}.plotclear")

                    # self.halg.net_add(pname, "vismach.plotclear")

                    for joint in range(6):
                        pname = gui_gen.draw_meter(f"Joint{joint + 1}", f"joint_pos{joint}", setup={"size": 100, "min": -360, "max": 360})
                        self.halg.net_add(f"joint.{joint}.pos-fb", pname, f"j{joint}pos-fb")
                        if joint == 2:
                            gui_gen.draw_hbox_end()
                            gui_gen.draw_hbox_begin()

                    gui_gen.draw_hbox_end()

                # buttons
                gui_gen.draw_frame_begin("MDI-Commands")
                gui_gen.draw_vbox_begin()

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
                                    if mdi_group_last == "Touch":
                                        pname = gui_gen.draw_led("", "probe-input")
                                        self.halg.net_add("motion.probe-input", pname)
                                    gui_gen.draw_hbox_end()
                                    gui_gen.draw_frame_end()
                                gui_gen.draw_frame_begin(mdi_group)
                                gui_gen.draw_hbox_begin()
                            else:
                                gui_gen.draw_hbox_end()
                                gui_gen.draw_frame_end()
                        mdi_title = command.split("|")[-1]
                        halpin = f"halui.mdi-command-{mdi_num:02d}"
                        pname = gui_gen.draw_button(mdi_title, halpin)
                        self.halg.net_add(pname, halpin)
                        mdi_group_last = mdi_group

                if mdi_group_last is not None:
                    if mdi_group_last == "Touch":
                        pname = gui_gen.draw_led("", "probe-input")
                        self.halg.net_add("motion.probe-input", pname)
                    gui_gen.draw_hbox_end()
                    gui_gen.draw_frame_end()

                gui_gen.draw_vbox_end()
                gui_gen.draw_frame_end()

                if linuxcnc_config.get("debug_info"):
                    gui_gen.draw_frame_begin("Debug-Info")
                    gui_gen.draw_vbox_begin()

                    pname = gui_gen.draw_number_s32("Servothread-Time", "servothreadtime")
                    self.halg.net_add("servo-thread.time", pname)

                    for axis_name, axis_config in self.project.axis_dict.items():
                        joints = axis_config["joints"]
                        for joint in joints:
                            pname = gui_gen.draw_number(f"J{joint}-Error", f"j{joint}error")
                            self.halg.net_add(f"joint.{joint}.f-error", pname)

                    gui_gen.draw_vbox_end()
                    gui_gen.draw_frame_end()

            for group in widgets.get(tab, {}):
                if group:
                    gui_gen.draw_frame_begin(group)
                    gui_gen.draw_vbox_begin()

                for widget in widgets[tab][group]:
                    section = widget["section"]
                    direction = widget["direction"]
                    boolean = widget["boolean"]
                    virtual = widget["virtual"]
                    group = widget["group"]
                    halname = widget["halname"]
                    netname = widget["netname"]
                    mapping = widget["mapping"]
                    setp = widget["setp"]
                    dtype = widget["dtype"]
                    displayconfig = widget["displayconfig"]

                    if dtype == "multilabel" and not boolean:
                        self.halextras.append(f"loadrt demux names=demux_{halname} personality={max(mapping.keys()) + 1}")
                        self.halextras.append(f"addf demux_{halname} servo-thread")
                        displayconfig["legends"] = []
                        lnum = 0
                        for value, text in mapping.items():
                            if lnum > 5:
                                break
                            displayconfig["legends"].append(text)
                            self.halg.net_add(f"demux_{halname}.out-{value:02d}", f"pyvcp.{halname}.legend{lnum}")

                            lnum += 1

                    title = displayconfig.get("title", haltitles.get(halname, halname))

                    # string len shortener
                    def short_str(halname):
                        for string, short in self.SHORTENER.items():
                            if len(halname) < 47 - len(self.gui_prefix):
                                break
                            halname = halname.replace(string, short)
                        return halname

                    # max = 47 characters
                    halname_short = short_str(halname)
                    halname_full = f"{self.gui_prefix}.{halname_short}"
                    if len(halname_short) >= 47 - len(self.gui_prefix):
                        riocore.log(f"ERROR: halname too long (>47): {halname_short} ({halname_full})")
                    gui_pinname = getattr(gui_gen, f"draw_{dtype}")(title, halname_short, setup=displayconfig)

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

                    if dtype == "multilabel" and not boolean:
                        self.halg.net_add(f"{halname}-u32-abs", f"demux_{halname}.sel-u32")
                    elif virtual and direction == "input":
                        self.halg.net_add(gui_pinname, f"riov.{halname}", f"sig_riov_{halname.replace('.', '_').replace('<', '-lt-').replace('>', '-gt-')}")
                    elif virtual and direction == "output":
                        self.halg.net_add(f"riov.{halname}", gui_pinname, f"sig_riov_{halname.replace('.', '_').replace('<', '-lt-').replace('>', '-gt-')}")
                    elif netname or setp or direction == "input":
                        self.halg.net_add(f"{halname}", gui_pinname)
                    elif direction == "output":
                        self.halg.net_add(gui_pinname, halname)

                if group:
                    gui_gen.draw_vbox_end()
                    gui_gen.draw_frame_end()

            gui_gen.draw_tab_end()

        gui_gen.draw_tabs_end()
        gui_gen.draw_end()
        gui_gen.save(self.configuration_path)

    def get_all_plugin_pins(self, configured=True, prefix=None):
        pins = []
        for plugin_instance in self.project.plugin_instances:
            for name, psetup in plugin_instance.plugin_setup.get("pins", {}).items():
                if name.startswith("SLOT:"):
                    continue
                pin = psetup.get("pin")
                rawpin = pin
                # filter unconfigured pins
                if configured and not pin:
                    continue

                pin_prefix = None
                if pin and ":" in pin:
                    pin_prefix = pin.split(":")[0]
                    # filter prefixes
                    pin = pin.split(":", 1)[1]

                elif pin and "." in pin:
                    pin_prefix = pin.split(".")[0]
                    # filter prefixes
                    pin = pin.split(".", 1)[1]

                if prefix and pin_prefix != prefix:
                    continue

                inverted = 0
                for modifier in psetup.get("modifier", []):
                    if modifier["type"] == "invert":
                        inverted = 1 - inverted
                if name not in plugin_instance.PINDEFAULTS:
                    continue
                direction = plugin_instance.PINDEFAULTS[name]["direction"]
                reset = plugin_instance.PINDEFAULTS[name].get("reset", False)
                pins.append(
                    {
                        "name": name,
                        "setup": psetup,
                        "rawpin": rawpin,
                        "pin": pin,
                        "prefix": pin_prefix,
                        "direction": direction,
                        "reset": reset,
                        "inverted": inverted,
                        "instance": plugin_instance,
                        "instance_title": plugin_instance.title,
                    }
                )
        return pins

    def hal(self):
        linuxcnc_config = self.project.config["jdata"].get("linuxcnc", {})
        gui = linuxcnc_config.get("gui", "axis")
        machinetype = linuxcnc_config.get("machinetype")
        embed_vismach = linuxcnc_config.get("embed_vismach")
        toolchange = linuxcnc_config.get("toolchange", "manual")

        # collect some hal-pin infos
        halpin_info = {}
        for plugin_instance in self.project.plugin_instances:
            if plugin_instance.plugin_setup.get("is_joint", False) is False:
                for signal_name, signal_config in plugin_instance.signals().items():
                    halname = signal_config["halname"]
                    netname = signal_config["netname"]
                    direction = signal_config["direction"]
                    userconfig = signal_config.get("userconfig", {})
                    boolean = signal_config.get("bool")
                    halpin_info[halname] = {
                        "direction": direction,
                        "boolean": boolean,
                    }

        components = {}
        for plugin_instance in self.project.plugin_instances:
            if plugin_instance.BASETHREAD:
                self.INI_DEFAULTS["EMCMOT"]["BASE_PERIOD"] = 25000
            if plugin_instance.COMPONENT:
                if plugin_instance.COMPONENT not in components:
                    components[plugin_instance.COMPONENT] = []
                components[plugin_instance.COMPONENT].append(plugin_instance)

        self.halg = hal_generator(halpin_info)

        self.halg.fmt_add_top("# load the realtime components")
        self.halg.fmt_add_top("loadrt [KINS]KINEMATICS")
        self.halg.fmt_add_top("loadrt [EMCMOT]EMCMOT base_period_nsec=[EMCMOT]BASE_PERIOD servo_period_nsec=[EMCMOT]SERVO_PERIOD num_joints=[KINS]JOINTS num_dio=[EMCMOT]NUM_DIO num_aio=[EMCMOT]NUM_AIO")
        self.halg.fmt_add_top("")

        # update pin-names for connected plugins
        for plugin_instance in self.project.plugin_instances:
            if hasattr(plugin_instance, "update_pins"):
                plugin_instance.update_pins(self)

        num_pids = self.num_joints
        self.halg.fmt_add_top("# pid controller")
        self.halg.fmt_add_top(f"loadrt pid num_chan={num_pids}")
        self.halg.fmt_add_top("")
        for pidn in range(num_pids):
            self.halg.fmt_add_top(f"addf pid.{pidn}.do-pid-calcs servo-thread")

        self.halg.fmt_add_top("addf motion-command-handler servo-thread")
        self.halg.fmt_add_top("addf motion-controller servo-thread")

        wcomps = {}
        for axis_name, axis_config in self.project.axis_dict.items():
            for joint_setup in axis_config["joints"]:
                joint = joint_setup["num"]
                maxsat = joint_setup.get("PID_MAXSATURATED")
                if maxsat:
                    wcomps[f"j{joint}maxsat"] = f"[JOINT_{joint}]MAXSATURATED"
                    self.halg.net_add(f"pid.{joint}.saturated-s", f"j{joint}maxsat.in", f"j{joint}sat")
                    self.halg.net_add(f"&j{joint}maxsat.out", "iocontrol.0.emc-enable-in")

        if wcomps:
            self.halg.fmt_add_top("# wcomp for saturated pid check")
            self.halg.fmt_add_top(f"loadrt wcomp names={''.join(list(wcomps))}")
            self.halg.fmt_add_top("")
            for name, wcomp in wcomps.items():
                self.halg.fmt_add_top(f"addf {name} servo-thread")
                self.halg.setp_add(f"{name}.min", -1.0)
                self.halg.setp_add(f"{name}.max", wcomp)

        if gui not in {"qtdragon", "qtdragon_hd"}:
            if toolchange == "manual":
                if gui == "gmoccapy":
                    self.halg.net_add("iocontrol.0.tool-prep-number", "gmoccapy.toolchange-number", "tool-prep-number")
                    self.halg.net_add("iocontrol.0.tool-change", "gmoccapy.toolchange-change", "tool-change")
                    self.halg.net_add("gmoccapy.toolchange-changed", "iocontrol.0.tool-changed", "tool-changed")
                    self.halg.net_add("iocontrol.0.tool-prepare", "iocontrol.0.tool-prepared", "tool-prepared")
                elif gui != "woodpecker":
                    self.halg.fmt_add_top("# manual toolchanger")
                    self.halg.fmt_add_top("loadusr -W hal_manualtoolchange")
                    self.halg.fmt_add_top("")
                    self.halg.net_add("iocontrol.0.tool-prep-number", "hal_manualtoolchange.number", "tool-prep-number")
                    self.halg.net_add("iocontrol.0.tool-change", "hal_manualtoolchange.change", "tool-change")
                    self.halg.net_add("hal_manualtoolchange.changed", "iocontrol.0.tool-changed", "tool-changed")
                    self.halg.net_add("iocontrol.0.tool-prepare", "iocontrol.0.tool-prepared", "tool-prepared")
            else:
                self.halg.net_add("iocontrol.0.tool-prepare", "iocontrol.0.tool-prepared", "tool-prepared")
                self.halg.net_add("iocontrol.0.tool-change", "iocontrol.0.tool-changed", "tool-changed")
        elif gui in {"qtdragon"}:
            self.halg.net_add("iocontrol.0.tool-prep-number", "hal_manualtoolchange.number", "tool-prep-number")
            self.halg.net_add("iocontrol.0.tool-change", "hal_manualtoolchange.change", "tool-change")
            self.halg.net_add("hal_manualtoolchange.changed", "iocontrol.0.tool-changed", "tool-changed")
            self.halg.net_add("iocontrol.0.tool-prepare", "iocontrol.0.tool-prepared", "tool-prepared")
        elif gui in {"qtdragon_hd"}:
            self.halg.net_add("iocontrol.0.tool-prep-number", "hal_manualtoolchange.number", "tool-prep-number")
            self.halg.net_add("iocontrol.0.tool-change", "hal_manualtoolchange.change", "tool-change")
            self.halg.net_add("hal_manualtoolchange.changed", "iocontrol.0.tool-changed", "tool-changed")
            self.halg.net_add("iocontrol.0.tool-prepare", "iocontrol.0.tool-prepared", "tool-prepared")
            for plugin_instance in self.project.plugin_instances:
                if plugin_instance.NAME != "modbus":
                    continue
                found_error_count = ""
                found_ampere = ""
                found_voltage = ""
                for signal_name, signal_config in plugin_instance.signals().items():
                    if signal_name.endswith("_error_count"):
                        found_error_count = signal_config["halname"]
                    elif signal_name.endswith("_ampere"):
                        found_ampere = signal_config["halname"]
                    elif signal_name.endswith("_dc_volt"):
                        found_voltage = signal_config["halname"]

                if found_error_count and found_ampere and found_voltage:
                    # self.halg.net_add(f"{found_error_count}-s32", "qtdragon.spindle-modbus-errors")
                    self.halg.net_add(found_ampere, "qtdragon.spindle-amps")
                    self.halg.net_add(found_voltage, "qtdragon.spindle-volts")
                    break

        self.mqtt_publisher = []
        for plugin_instance in self.project.plugin_instances:
            for signal_name, signal_config in plugin_instance.signals().items():
                halname = signal_config["halname"]
                userconfig = signal_config.get("userconfig", {})
                mqtt = userconfig.get("mqtt")
                direction = signal_config["direction"]
                if mqtt:
                    self.mqtt_publisher.append(halname)
        if self.mqtt_publisher:
            self.halg.fmt_add_top("# mqtt-publisher")
            self.halg.fmt_add_top("loadusr -W mqtt-publisher [MQTT]DRYRUN --mqtt-broker=[MQTT]BROKER \\")
            self.halg.fmt_add_top("--mqtt-user=[MQTT]USERNAME --mqtt-password=[MQTT]PASSWORD keys=\\")
            self.halg.fmt_add_top(",".join(self.mqtt_publisher))
            self.halg.fmt_add_top("")

        linuxcnc_setp = {}

        if machinetype == "corexy":
            self.halg.fmt_add_top("# machinetype is corexy")
            self.halg.fmt_add_top("loadrt corexy_by_hal names=corexy")
            self.halg.fmt_add_top("")
            self.halg.fmt_add_top("addf corexy servo-thread")
        elif machinetype == "ldelta":
            self.halg.fmt_add_top("# loading lineardelta gl-view")
            self.halg.fmt_add_top("loadusr -W lineardelta MIN_JOINT=-420")
            self.halg.fmt_add_top("")
        elif machinetype == "rdelta":
            self.halg.fmt_add_top("# loading rotarydelta gl-view")
            self.halg.fmt_add_top("loadusr -W rotarydelta MIN_JOINT=-420")
            self.halg.fmt_add_top("")
        elif machinetype in {"melfa", "melfa_nogl"}:
            if machinetype != "melfa_nogl":
                self.halg.fmt_add_top("# loading melfa gui")
                self.halg.fmt_add_top("loadusr -W melfagui")
                self.halg.fmt_add_top("")

            self.halg.fmt_add_top("net :kinstype-select <= motion.analog-out-03 => motion.switchkins-type")
            os.makedirs(self.configuration_path, exist_ok=True)

            for source in glob.glob(os.path.join(riocore_path, "files", "melfa", "*")):
                basename = os.path.basename(source)
                target = os.path.join(self.configuration_path, basename)
                if os.path.isfile(source):
                    shutil.copy(source, target)
                elif not os.path.isdir(target):
                    shutil.copytree(source, target)

            if machinetype != "melfa_nogl":
                for joint in range(6):
                    self.halg.net_add(f"joint.{joint}.pos-fb", f"melfagui.joint{joint + 1}", f"j{joint}pos-fb")

            if linuxcnc_config.get("flexbot"):
                for joint in range(len(self.project.axis_dict)):
                    self.halg.net_add(f"joint.{joint}.pos-fb", f"flexhal.joint{joint + 1}", f"j{joint}pos-fb")

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
                for joint in range(len(self.project.axis_dict)):
                    if machinetype in {"melfa", "melfa_nogl"}:
                        # melfa has some inverted joints
                        if joint in {1, 2, 3}:
                            self.halg.net_add(f"(joint.{joint}.pos-fb * -1)", f"{embed_vismach}.joint{joint + 1}")
                        else:
                            self.halg.net_add(f"joint.{joint}.pos-fb", f"{embed_vismach}.joint{joint + 1}", f"j{joint}pos-fb")
                    else:
                        self.halg.net_add(f"joint.{joint}.pos-fb", f"{embed_vismach}.joint{joint + 1}", f"j{joint}pos-fb")

        linuxcnc_setp.update(linuxcnc_config.get("setp", {}))
        for key, value in linuxcnc_setp.items():
            self.halg.setp_add(f"{key}", value)

        for net in linuxcnc_config.get("net", []):
            net_source = net.get("source")
            net_target = net.get("target")
            net_name = net.get("name") or None
            if net_source and net_target:
                self.halg.net_add(f"({net_source})", net_target, net_name)

        for plugin_instance in self.project.plugin_instances:
            for name in plugin_instance.FILES:
                plugin_path = os.path.join(riocore_path, "plugins", plugin_instance.NAME)
                source = os.path.join(plugin_path, name)
                target = os.path.join(self.configuration_path, name)
                if os.path.isfile(source):
                    shutil.copy(source, target)
                    if source.endswith((".py", ".sh")):
                        os.chmod(target, stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR | stat.S_IRGRP | stat.S_IXGRP | stat.S_IROTH | stat.S_IXOTH)
                elif not os.path.isdir(target):
                    shutil.copytree(source, target)

        # run the component loaders
        for component_type, instances in components.items():
            if hasattr(instances[0], "component_loader"):
                ret = instances[0].component_loader(instances)
                if ret:
                    self.halg.fmt_add_top(ret)

        # run extra_files
        for component_type, instances in components.items():
            if hasattr(instances[0], "extra_files"):
                instances[0].extra_files(self, instances)

        # generate special hal entries for each plugin
        for plugin_instance in self.project.plugin_instances:
            if hasattr(plugin_instance, "hal"):
                plugin_instance.hal(self)

        # TODO: can be removed if all addons moved to plugins
        # generate special hal entries for each addon
        for addon_name, addon in self.addons.items():
            if hasattr(addon, "hal"):
                addon.hal(self)

        # adding all configured setp and net pins/signals
        for plugin_instance in self.project.plugin_instances:
            if plugin_instance.plugin_setup.get("is_joint", False) is True:
                # only setp for joints, other handled by plugin_instance.hal()
                for signal_name, signal_config in plugin_instance.signals().items():
                    halname = signal_config["halname"]
                    userconfig = signal_config.get("userconfig", {})
                    setp = userconfig.get("setp")
                    rprefix = "rio"
                    if setp:
                        self.halg.setp_add(f"{rprefix}.{halname}", setp)
            else:
                for signal_name, signal_config in plugin_instance.signals().items():
                    halname = signal_config["halname"]
                    netname = signal_config["netname"]
                    userconfig = signal_config.get("userconfig", {})
                    scale = userconfig.get("scale")
                    offset = userconfig.get("offset")
                    setp = userconfig.get("setp")
                    direction = signal_config["direction"]
                    virtual = signal_config.get("virtual")
                    comp = signal_config.get("component")
                    rprefix = ""
                    if virtual:
                        rprefix = "riov."
                    if scale and not virtual:
                        self.halg.setp_add(f"{rprefix}{halname}-scale", scale)
                    if offset and not virtual:
                        self.halg.setp_add(f"{rprefix}{halname}-offset", offset)
                    if netname:
                        if direction == "inout":
                            self.halg.fmt_add(f"net rios.{halname} {rprefix}.{halname} <=> {netname}")
                        elif direction == "input":
                            for net in netname.split(","):
                                net = net.strip()
                                net_type = halpins.LINUXCNC_SIGNALS[direction].get(net, {}).get("type", float)
                                if net_type is int:
                                    self.halg.net_add(f"{rprefix}{halname}-s32", net)
                                else:
                                    self.halg.net_add(f"{rprefix}{halname}", net)
                        elif direction == "output":
                            target = f"{rprefix}{halname}"
                            self.halg.net_add(netname, f"{rprefix}{halname}")
                    elif setp:
                        self.halg.setp_add(f"{rprefix}{halname}", setp)
                    elif virtual and comp:
                        if direction == "input":
                            self.halg.net_add(f"{rprefix}{halname}", halname)
                        else:
                            self.halg.net_add(halname, f"{rprefix}{halname}")

        found_user_anbale = False
        for value in self.halg.signals_out.values():
            if "iocontrol.0.user-enable-out" in value["expression"]:
                found_user_anbale = True
        if not found_user_anbale:
            self.halg.net_add("&iocontrol.0.user-enable-out", "iocontrol.0.emc-enable-in", "user-enable-out")

    def create_axis_config(self, project, prefix=""):
        linuxcnc_config = project.config["jdata"].get("linuxcnc", {})
        machinetype = linuxcnc_config.get("machinetype")
        axis_names = "XYZACBUVW"
        if machinetype in {"melfa", "melfa_nogl", "puma"}:
            axis_names = "XYZABC"

        axis_config = {}
        for plugin_instance in project.plugin_instances:
            if plugin_instance.plugin_setup.get("is_joint", False):
                axis_name = plugin_instance.plugin_setup.get("axis")
                if axis_name:
                    if axis_name not in axis_config:
                        axis_config[axis_name] = {"joints": []}
                    axis_config[axis_name]["joints"].append({"instance": plugin_instance})

        for plugin_instance in project.plugin_instances:
            if plugin_instance.plugin_setup.get("is_joint", False):
                axis_name = plugin_instance.plugin_setup.get("axis")
                if not axis_name:
                    for name in axis_names:
                        if name not in axis_config:
                            axis_name = name
                            break
                    if axis_name:
                        if axis_name not in axis_config:
                            axis_config[axis_name] = {"joints": []}
                        axis_config[axis_name]["joints"].append({"instance": plugin_instance})

        homeswitches = {}
        for plugin_instance in project.plugin_instances:
            if plugin_instance.plugin_setup.get("is_joint", False) is False:
                for signal_name, signal_config in plugin_instance.signals().items():
                    userconfig = signal_config.get("userconfig")
                    net = userconfig.get("net")
                    if net and net.startswith("joint.") and net.endswith(".home-sw-in"):
                        homeswitches[int(net.split(".")[1])] = plugin_instance

        joint_num = 0
        for axis in axis_names:
            for axis_name, axis_data in axis_config.items():
                if axis != axis_name:
                    continue
                if machinetype == "lathe":
                    home_sequence_default = 2
                    if axis_name == "X":
                        home_sequence_default = 1
                elif machinetype in {"melfa", "melfa_nogl"}:
                    home_sequence_default = 2
                    if axis_name == "X":
                        home_sequence_default = 2
                    elif axis_name == "Y" or axis_name == "Z" or axis_name == "A":
                        home_sequence_default = 1
                    elif axis_name == "B":
                        home_sequence_default = 2
                    elif axis_name == "C":
                        home_sequence_default = 1
                elif axis_name == "Z":
                    home_sequence_default = 1
                elif len(axis_data["joints"]) > 1:
                    home_sequence_default = -2
                else:
                    home_sequence_default = 2

                for joint_data in axis_data["joints"]:
                    joint_data["axis"] = axis_name
                    joint_data["num"] = joint_num
                    joint_data["mode"] = joint_data["instance"].JOINT_MODE
                    if joint_num in homeswitches:
                        joint_data["homeswitch"] = homeswitches[joint_num]
                    else:
                        joint_data["homeswitch"] = None
                        home_sequence_default = 0

                    # copy defaults
                    for key, value in self.JOINT_DEFAULTS.items():
                        joint_data[key.upper()] = value
                    joint_data["HOME_SEQUENCE"] = home_sequence_default

                    if machinetype not in {"scara", "melfa", "melfa_nogl", "puma", "lathe"}:
                        if axis_name in {"Z"}:
                            joint_data["HOME_SEARCH_VEL"] *= -1.0
                            joint_data["HOME_LATCH_VEL"] *= -1.0
                            joint_data["MAX_VELOCITY"] /= 3.0

                    if joint_data["homeswitch"] is None:
                        joint_data["HOME_SEARCH_VEL"] = 0.0
                        joint_data["HOME_LATCH_VEL"] = 0.0
                        joint_data["HOME_FINAL_VEL"] = 0.0
                        joint_data["HOME_OFFSET"] = 0
                        joint_data["HOME"] = 0.0
                        joint_data["HOME_SEQUENCE"] = 0

                    if machinetype in {"scara"}:
                        if axis_name in {"Z"}:
                            joint_data["TYPE"] = "LINEAR"
                        else:
                            joint_data["TYPE"] = "ANGULAR"
                    elif machinetype in {"melfa", "melfa_nogl", "puma"} or axis_name in {"A", "C", "B"}:
                        joint_data["TYPE"] = "ANGULAR"
                    else:
                        joint_data["TYPE"] = "LINEAR"

                    feedback = joint_data["instance"].plugin_setup.get("joint", {}).get("feedback", "")
                    if feedback:
                        if ":" in feedback:
                            fb_plugin_name, fb_signal_name = feedback.split(":")
                        else:
                            fb_plugin_name = feedback
                            fb_signal_name = "position"
                        found = None
                        for sub_instance in project.plugin_instances:
                            if sub_instance.title == fb_plugin_name:
                                for sub_signal_name, sub_signal_config in sub_instance.signals().items():
                                    if fb_signal_name != sub_signal_name:
                                        continue
                                    sub_direction = sub_signal_config["direction"]
                                    if sub_direction != "input":
                                        riocore.log("ERROR: can not use this as feedback (no input signal):", sub_signal_config)
                                        exit(1)
                                    feedback_halname = f"{prefix}{sub_signal_config['halname']}"
                                    feedback_signal = feedback_halname.split(".")[-1]
                                    sub_signals_setup = sub_instance.plugin_setup.get("signals", {})
                                    feedback_scale = float(sub_signals_setup.get(feedback_signal, {}).get("scale", 1.0))
                                    if "signals" not in sub_instance.plugin_setup:
                                        sub_instance.plugin_setup["signals"] = {}
                                    if feedback_signal not in sub_instance.plugin_setup["signals"]:
                                        sub_instance.plugin_setup["signals"][feedback_signal] = {}
                                    joint_data["feedback_name"] = fb_plugin_name
                                    joint_data["feedback_halname"] = feedback_halname
                                    joint_data["feedback_scale_halname"] = f"{feedback_halname}-scale"
                                    joint_data["feedback_signal"] = fb_signal_name
                                    joint_data["feedback_instance"] = sub_instance
                                    joint_data["feedback_setup"] = sub_instance.plugin_setup["signals"][feedback_signal]
                                    joint_data["SCALE_IN"] = feedback_scale
                                    found = True
                                    break
                        if found:
                            joint_data["mode"] = "velocity"
                        else:
                            riocore.log(f"ERROR: feedback {fb_plugin_name}->{fb_signal_name} for joint {joint_num} not found")

                    # overwrite with user configuration
                    joint_config = joint_data["instance"].plugin_setup.get("joint", {})
                    for key, value in joint_config.items():
                        key = key.upper()
                        key = {"SCALE": "SCALE_OUT"}.get(key, key)
                        joint_data[key] = value

                    if not feedback:
                        joint_data["SCALE_IN"] = joint_data["SCALE_OUT"]

                    joint_data["instance"].plugin_setup["joint_data"] = joint_data
                    joint_num += 1

                # overwrite axis configuration with user data
                for key, value in linuxcnc_config.get("axis", {}).get(axis_name, {}).items():
                    key = key.upper()
                    axis_data[key] = value

        return axis_config
