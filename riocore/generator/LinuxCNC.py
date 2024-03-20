import copy
import glob
import importlib
import os
import sys

from riocore import halpins

riocore_path = os.path.dirname(os.path.dirname(__file__))


class LinuxCNC:
    AXIS_NAMES = ["X", "Y", "Z", "A", "C", "B", "U", "V", "W"]
    AXIS_DEFAULTS = {
        "MAX_VELOCITY": 40.0,
        "MAX_ACCELERATION": 500.0,
        "MIN_LIMIT": -500,
        "MAX_LIMIT": 1500,
        "MIN_FERROR": 0.01,
        "FERROR": 1.0,
        "BACKLASH": 0.0,
    }
    PID_DEFAULTS = {
        "P": 50.0,
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
        "HOME": 0.0,
        "MIN_LIMIT": -500.0,
        "MAX_LIMIT": 1500.0,
        "MAX_VELOCITY": 40.0,
        "MAX_ACCELERATION": 500.0,
        "STEPGEN_MAXACCEL": 2000.0,
        "SCALE_OUT": 320.0,
        "SCALE_IN": 320.0,
        "HOME_SEARCH_VEL": 20.0,
        "HOME_LATCH_VEL": 3.0,
        "HOME_FINAL_VEL": -20,
        "HOME_IGNORE_LIMITS": "YES",
        "HOME_USE_INDEX": "NO",
        "HOME_OFFSET": 1.0,
        "HOME": 0.0,
        "HOME_SEQUENCE": -1,
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
            "PYVCP": "rio-gui.xml",
            "PREFERENCE_FILE_PATH": None,
            "ARCDIVISION": 64,
            "GRIDS": "10mm 20mm 50mm 100mm",
            "INTRO_GRAPHIC": "linuxcnc.gif",
            "INTRO_TIME": 2,
            "PROGRAM_PREFIX": "~/linuxcnc/nc_files",
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
            "MAX_LINEAR_VELOCITY": 80.0,
            "MIN_ANGULAR_VELOCITY": 0.0,
            "DEFAULT_ANGULAR_VELOCITY": 2.5,
            "MAX_ANGULAR_VELOCITY": 5.0,
            "PYVCP_POSITION": "RIGHT",
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
        "HALUI": {
            "MDI_COMMAND|00": "G92 X0",
            "MDI_COMMAND|01": "G92 Y0",
            "MDI_COMMAND|02": "G92 Z0",
            "MDI_COMMAND|03": "G92 X0 Y0",
            "MDI_COMMAND|04": "o<z_touch> call",
            "MDI_COMMAND|05": "o<x_touch> call",
        },
        "TRAJ": {
            "COORDINATES": None,
            "LINEAR_UNITS": "mm",
            "ANGULAR_UNITS": "degree",
            "CYCLE_TIME": 0.010,
            "DEFAULT_LINEAR_VELOCITY": 50.00,
            "MAX_LINEAR_VELOCITY": 50.00,
            "NO_FORCE_HOMING": 1,
        },
        "EMCIO": {
            "EMCIO": "io",
            "CYCLE_TIME": 0.100,
            "TOOL_TABLE": "tool.tbl",
        },
    }

    def __init__(self, project):
        self.postgui_call_list = []
        self.pregui_call_list = []
        self.loadrts = []
        self.axisout = []
        self.networks = {}
        self.setps = {}
        self.project = project
        self.base_path = f"{self.project.config['output_path']}/LinuxCNC"
        self.component_path = f"{self.base_path}"
        self.configuration_path = f"{self.base_path}"
        self.create_axis_config()
        self.addons = {}
        for addon_path in glob.glob(f"{riocore_path}/generator/addons/*/linuxcnc.py"):
            addon_name = addon_path.split("/")[-2]
            self.addons[addon_name] = importlib.import_module(".linuxcnc", f"riocore.generator.addons.{addon_name}")

    def generator(self):
        self.component()
        self.hal()
        self.gui()
        for addon_name, addon in self.addons.items():
            if hasattr(addon, "generator"):
                addon.generator(self)
        self.misc()
        self.ini()
        os.system(f"mkdir -p {self.configuration_path}/")
        output_hal = []
        output_postgui = []
        output_hal += self.loadrts

        custom_filter = ("pyvcp", "qtdragon", "axisui", "mpg")
        ctypes = {"AND": 0x100, "OR": 0x200, "XOR": 0x400, "NAND": 0x800, "NOR": 0x1000}

        jdata = self.project.config["jdata"]
        linuxcnc_config = jdata.get("linuxcnc", {})
        for network, net in linuxcnc_config.get("halsignals", {}).items():
            self.networks[network] = net

        # hal
        # signal_prefix = "rios."
        signal_prefix = ""
        for network, net in self.networks.items():
            if net["in"] and net["out"]:
                output_hal.append("")
                output_hal.append(f"# {network}")
                output_postgui.append("")
                output_postgui.append(f"# {network}")

                if len(net["in"]) == 1:
                    if not net["in"][0].startswith(custom_filter):
                        output_hal.append(f"net {signal_prefix}{network} <= {net['in'][0]}")
                    else:
                        output_postgui.append(f"net {signal_prefix}{network} <= {net['in'][0]}")
                    for out in net["out"]:
                        if not out.startswith(custom_filter):
                            output_hal.append(f"net {signal_prefix}{network} => {out}")
                        else:
                            output_postgui.append(f"net {signal_prefix}{network} => {out}")
                else:
                    uniq_types = set()
                    if net["in"][0].endswith("counts"):
                        if len(net["in"]) > 4:
                            print(f"ERROR: can only sum 4 integer values: {net}")

                        output_hal.append(f"loadrt scaled_s32_sums names=isum.{network}")
                        output_hal.append(f"addf isum.{network} servo-thread")
                        for in_n, pin_in in enumerate(net["in"]):
                            if not pin_in.startswith(custom_filter):
                                output_hal.append(f"net {signal_prefix}{network}-in-{in_n} <= {pin_in}")
                                output_hal.append(f"net {signal_prefix}{network}-in-{in_n} => isum.{network}.in{in_n}")
                            else:
                                output_postgui.append(f"net {signal_prefix}{network}-in-{in_n} <= {pin_in}")
                                output_postgui.append(f"net {signal_prefix}{network}-in-{in_n} => isum.{network}.in{in_n}")
                        output_hal.append(f"net {signal_prefix}{network}_out-s <= isum.{network}.out-s")
                        for out in net["out"]:
                            ctype = net["options"].get(out, {}).get("type", "OR")
                            if not out.startswith(custom_filter):
                                output_hal.append(f"net {signal_prefix}{network}_out-s => {out}")
                            else:
                                output_postgui.append(f"net {signal_prefix}{network}_out-s => {out}")
                    else:
                        for option in net["options"].values():
                            uniq_types.add(option["type"])

                        personality = 0x0
                        for ctype in uniq_types:
                            personality |= ctypes[ctype]

                        n_inputs = len(net["in"])
                        output_hal.append(f"loadrt logic names=logic.{network} personality=0x{personality+n_inputs:x}")
                        output_hal.append(f"addf logic.{network} servo-thread")
                        for in_n, pin_in in enumerate(net["in"]):
                            if not pin_in.startswith(custom_filter):
                                output_hal.append(f"net {signal_prefix}{network}-in-{in_n:02d} <= {pin_in}")
                                output_hal.append(f"net {signal_prefix}{network}-in-{in_n:02d} => logic.{network}.in-{in_n:02d}")
                            else:
                                output_postgui.append(f"net {signal_prefix}{network}-in-{in_n:02d} <= {pin_in}")
                                output_postgui.append(f"net {signal_prefix}{network}-in-{in_n:02d} => logic.{network}.in-{in_n:02d}")

                        for ctype in uniq_types:
                            output_hal.append(f"net {signal_prefix}{network}_{ctype.lower()} <= logic.{network}.{ctype.lower()}")

                        for out in net["out"]:
                            ctype = net["options"].get(out, {}).get("type", "OR")
                            if not out.startswith(custom_filter):
                                output_hal.append(f"net {signal_prefix}{network}_{ctype.lower()} => {out}")
                            else:
                                output_postgui.append(f"net {signal_prefix}{network}_{ctype.lower()} => {out}")

        for name, value in self.setps.items():
            # check if pin is connected to other pin
            isFree = True
            for network, net in self.networks.items():
                if net["in"] and net["out"]:
                    if name in net["out"]:
                        isFree = False
                        break
            if isFree:
                if not name.startswith(custom_filter):
                    output_hal.append(f"setp {name} {value}")
                else:
                    output_postgui.append(f"setp {name} {value}")

        output_hal.append("")
        output_hal += self.axisout
        open(f"{self.configuration_path}/rio.hal", "w").write("\n".join(output_hal))
        open(f"{self.configuration_path}/custom_postgui.hal", "w").write("\n".join(output_postgui))

        extra_data = []
        if os.path.isfile(f"{self.configuration_path}/postgui_call_list.hal"):
            # read existing file to keep custom entry's
            cl_data = open(f"{self.configuration_path}/postgui_call_list.hal", "r").read()
            for line in cl_data.split("\n"):
                if line.startswith("source "):
                    source = " ".join(line.split()[1:])
                    if source in self.postgui_call_list:
                        continue
                extra_data.append(line.strip())
        cl_output = []
        for halfile in self.postgui_call_list:
            cl_output.append(f"source {halfile}")
        for line in extra_data:
            cl_output.append(line)
        open(f"{self.configuration_path}/postgui_call_list.hal", "w").write("\n".join(cl_output))

        extra_data = []
        if os.path.isfile(f"{self.configuration_path}/pregui_call_list.hal"):
            # read existing file to keep custom entry's
            cl_data = open(f"{self.configuration_path}/pregui_call_list.hal", "r").read()
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
        open(f"{self.configuration_path}/pregui_call_list.hal", "w").write("\n".join(cl_output))

        print(f"writing linuxcnc files to: {self.base_path}")

    def ini_mdi_command(self, command):
        jdata = self.project.config["jdata"]
        ini = self.ini_defaults(jdata, num_joints=5, axis_dict=self.axis_dict)
        mdi_index = ""
        mdi_n = 0
        for key, value in ini["HALUI"].items():
            if key.startswith("MDI_COMMAND|"):
                if value == command:
                    mdi_index = mdi_n
                    break
                mdi_n += 1
        if not mdi_index:
            mdi_index = mdi_n
            ini["HALUI"][f"MDI_COMMAND|{mdi_index:02d}"] = command
        return f"halui.mdi-command-{mdi_index:02d}"

    @classmethod
    def ini_defaults(cls, jdata, num_joints=5, axis_dict={}):
        linuxcnc_config = jdata.get("linuxcnc", {})
        ini_setup = cls.INI_DEFAULTS.copy()
        gui = jdata.get("gui", "axis")
        machinetype = jdata.get("machinetype")

        if machinetype == "lathe":
            ini_setup["DISPLAY"]["LATHE"] = 1

        coordinates = []
        for axis_name, joints in axis_dict.items():
            for joint, joint_setup in joints.items():
                coordinates.append(axis_name)

        kinematics = "trivkins"
        ini_setup["KINS"]["JOINTS"] = num_joints
        ini_setup["KINS"]["KINEMATICS"] = f"{kinematics} coordinates={''.join(coordinates)}"
        ini_setup["TRAJ"]["COORDINATES"] = "".join(coordinates)
        ini_setup["EMCMOT"]["NUM_DIO"] = 3
        ini_setup["EMCMOT"]["NUM_AIO"] = 3

        if gui in {"tklinuxcnc", "touchy", "probe_basic"}:
            ini_setup["DISPLAY"]["DISPLAY"] = gui
        elif gui == "qtdragon":
            qtdragon_setup = {
                "DISPLAY": {
                    "DISPLAY": "qtvcp -d rio_hd",
                    "ICON": "silver_dragon.png",
                    "EDITOR": None,
                    "PYVCP": None,
                    "PREFERENCE_FILE_PATH": "WORKINGFOLDER/qtdragon_hd.pref",
                    "INTRO_GRAPHIC": "silver_dragon.png",
                    "CYCLE_TIME": 100,
                    "NGCGUI_SUBFILE_PATH": "../../../nc_files/ngcgui_lib/",
                    "NGCGUI_SUBFILE": "qpocket.ngc",
                    "MDI_HISTORY_FILE": "mdi_history.dat",
                    "LOG_FILE": "qtdragon_hd.log",
                },
                "MDI_COMMAND_LIST": {
                    "MDI_COMMAND": [
                        "G0 Z25 X0 Y0;Z0,Goto\\nZero",
                        "G53 G0 Z0;G53 G0 X0 Y0,Goto\\nMach\\nZero",
                    ],
                },
                "FILTER": {
                    "PROGRAM_EXTENSION": [
                        ".ngc,.nc,.tap G-Code File (*.ngc,*.nc,*.tap)",
                        ".png,.gif,.jpg Greyscale Depth Image",
                        ".py Python Script",
                    ],
                    "png": "image-to-gcode",
                    "gif": "image-to-gcode",
                    "jpg": "image-to-gcode",
                    "py": "python3",
                },
                "RS274NGC": {
                    "PARAMETER_FILE": "linuxcnc.var",
                    "RS274NGC_STARTUP_CODE": "G17 G21 G40 G43H0 G54 G64P0.0127 G80 G90 G94 G97 M5 M9",
                    "SUBROUTINE_PATH": "./subroutines/",
                    "USER_M_PATH": "./mcodes/",
                    "ON_ABORT_COMMAND": "O <on_abort> call",
                },
                "HALUI": {},
                "PROBE": {
                    "USE_PROBE": "basicprobe",
                },
            }
            for section, sdata in qtdragon_setup.items():
                if section not in ini_setup:
                    ini_setup[section] = {}
                for key, value in sdata.items():
                    ini_setup[section][key] = value

        return ini_setup

    def ini(self):
        jdata = self.project.config["jdata"]
        linuxcnc_config = jdata.get("linuxcnc", {})
        gui = self.project.config["jdata"].get("gui", "axis")
        machinetype = self.project.config["jdata"].get("machinetype")
        ini_setup = self.ini_defaults(self.project.config["jdata"], num_joints=self.num_joints, axis_dict=self.axis_dict)

        for section, section_options in self.project.config["jdata"].get("linuxcnc", {}).get("ini", {}).items():
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
                    output.append(f"{key} = {value}")
            output.append("")

        for axis_name, joints in self.axis_dict.items():
            output.append(f"[AXIS_{axis_name}]")
            axis_setup = copy.deepcopy(self.AXIS_DEFAULTS)
            axis_max_velocity = 10000.0
            axis_max_acceleration = 10000.0
            axis_min_limit = 100000.0
            axis_max_limit = -100000.0
            axis_backlash = 0.0
            for joint, joint_setup in joints.items():
                max_velocity = joint_setup["MAX_VELOCITY"]
                max_acceleration = joint_setup["MAX_ACCELERATION"]
                min_limit = joint_setup["MIN_LIMIT"]
                max_limit = joint_setup["MAX_LIMIT"]
                backlash = joint_setup.get("BACKLASH", 0.0)
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

                axis_setup["MAX_VELOCITY"] = axis_max_velocity
                axis_setup["MAX_ACCELERATION"] = axis_max_acceleration
                axis_setup["MIN_LIMIT"] = axis_min_limit
                axis_setup["MAX_LIMIT"] = axis_max_limit
                axis_setup["BACKLASH"] = backlash

            for key, value in axis_setup.items():
                output.append(f"{key:18s} = {value}")
            output.append("")
            for joint, joint_config in joints.items():
                position_mode = joint_config["position_mode"]
                position_halname = joint_config["position_halname"]
                feedback_halname = joint_config["feedback_halname"]
                enable_halname = joint_config["enable_halname"]
                plugin_instance = joint_config["plugin_instance"]
                pin_num = joint_config["pin_num"]

                output.append(f"[JOINT_{joint}]")
                output.append(f"# {plugin_instance.instances_name}")
                if position_mode == "absolute":
                    for key, value in joint_setup.items():
                        if key in self.JOINT_DEFAULTS:
                            output.append(f"{key:18s} = {value}")

                elif position_halname and feedback_halname:
                    pid_setup = self.PID_DEFAULTS.copy()
                    for key, value in pid_setup.items():
                        output.append(f"{key:18s} = {value}")
                    output.append("")
                    for key, value in joint_setup.items():
                        if key in self.JOINT_DEFAULTS:
                            output.append(f"{key:18s} = {value}")
                output.append("")

        os.system(f"mkdir -p {self.configuration_path}/")
        open(f"{self.configuration_path}/rio.ini", "w").write("\n".join(output))

    def misc(self):
        if not os.path.isfile(f"{self.configuration_path}/tool.tbl"):
            tooltbl = []
            tooltbl.append("T1 P1 D0.125000 Z+0.511000 ;1/8 end mill")
            tooltbl.append("T2 P2 D0.062500 Z+0.100000 ;1/16 end mill")
            tooltbl.append("T3 P3 D0.201000 Z+1.273000 ;#7 tap drill")
            os.system(f"mkdir -p {self.configuration_path}/")
            open(f"{self.configuration_path}/tool.tbl", "w").write("\n".join(tooltbl))

    def hal_setp_add(self, output_name, value):
        if output_name not in self.setps:
            self.setps[output_name] = value
        # else:
        #     print(f"WARNING: {output_name} allready set to {self.setps[output_name]}")

    def hal_net_add(self, input_name, output_name, signal_name=None):
        ctype = "OR"
        if output_name[0] == "&":
            ctype = "AND"
            output_name = output_name[1:]
        elif output_name[0] == "|":
            ctype = "OR"
            output_name = output_name[1:]
        elif output_name[0] == "^":
            ctype = "XOR"
            output_name = output_name[1:]
        network = None

        for net_name, net_nodes in self.networks.items():
            if input_name in net_nodes["in"]:
                network = net_name
            elif input_name in net_nodes["out"]:
                network = net_name
            elif output_name in net_nodes["out"]:
                network = net_name
                break
            elif output_name == net_nodes["in"][0]:
                network = net_name
                self.networks[network]["in"] = [input_name]
            elif output_name == net_nodes["in"]:
                print(f"ERROR: can not handle this constellation {input_name} -> {output_name}: output is allready in a multi input signal")

        if not network:
            if signal_name in self.networks:
                print(f"ERROR: signal name '{signal_name}' already exist")
                signal_name = None

            if signal_name:
                # using user defined signal name
                network = signal_name
            else:
                if not input_name.startswith("rio."):
                    network = input_name.replace(".", "-")
                else:
                    network = output_name.replace(".", "-")
            if network not in self.networks:
                self.networks[network] = {
                    "in": [input_name],
                    "out": [],
                    "type": ctype,
                    "options": {},
                }

        if output_name not in self.networks[network]["out"]:
            self.networks[network]["out"].append(output_name)
            self.networks[network]["options"][output_name] = {"type": ctype}
        elif input_name not in self.networks[network]["in"]:
            self.networks[network]["in"].append(input_name)

    def gui(self):
        os.system(f"mkdir -p {self.configuration_path}/")
        machinetype = self.project.config["jdata"].get("machinetype")
        gui = self.project.config["jdata"].get("gui", "axis")
        if gui == "qtdragon":
            self.gui_gen = qtdragon()
            prefix = "qtdragon"
        else:
            self.gui_gen = axis()
            prefix = "pyvcp"

        custom = []
        self.cfgxml_data = {
            "status": [],
        }
        for plugin_instance in self.project.plugin_instances:
            if plugin_instance.plugin_setup.get("is_joint", False) is False:
                for signal_name, signal_config in plugin_instance.signals().items():
                    userconfig = signal_config.get("userconfig", {})
                    displayconfig = userconfig.get("display", signal_config.get("display", {}))
                    section = displayconfig.get("section")
                    if section and section not in self.cfgxml_data:
                        self.cfgxml_data[section] = []
        self.cfgxml_data["inputs"] = []
        self.cfgxml_data["outputs"] = []

        # buttons
        if gui != "qtdragon":
            self.cfgxml_data["status"].append('  <labelframe text="MDI-Commands">')
            self.cfgxml_data["status"].append("    <relief>RAISED</relief>")
            self.cfgxml_data["status"].append('    <font>("Helvetica", 10)</font>')
            self.cfgxml_data["status"].append("    <hbox>")
            self.cfgxml_data["status"].append("      <relief>RIDGE</relief>")
            self.cfgxml_data["status"].append("      <bd>2</bd>")
            if machinetype == "lathe":
                if "Z":
                    halpin = self.ini_mdi_command("G92 Z0")
                    self.hal_net_add(f"{prefix}.zeroz", halpin, "zero-z")
                    self.cfgxml_data["status"] += self.gui_gen.draw_button("zero-z", "zeroz")
                if "X":
                    halpin = self.ini_mdi_command("G92 X0")
                    self.hal_net_add(f"{prefix}.zerox", halpin, "zero-x")
                    self.cfgxml_data["status"] += self.gui_gen.draw_button("zero-x", "zerox")
                    halpin = self.ini_mdi_command("o<z_touch> call")
                    self.hal_net_add(f"{prefix}.touchx", halpin, "touch-x")
                    self.cfgxml_data["status"] += self.gui_gen.draw_button("touch-x", "touchx")
            else:
                if "X" in self.axis_dict and "Y" in self.axis_dict:
                    halpin = self.ini_mdi_command("G92 X0 Y0")
                    self.hal_net_add(f"{prefix}.zeroxy", halpin, "zero-xy")
                    self.cfgxml_data["status"] += self.gui_gen.draw_button("zero-xy", "zeroxy")
                if "Z":
                    halpin = self.ini_mdi_command("G92 Z0")
                    self.hal_net_add(f"{prefix}.zeroz", halpin, "zero-z")
                    self.cfgxml_data["status"] += self.gui_gen.draw_button("zero-z", "zeroz")

            self.cfgxml_data["status"].append("    </hbox>")
            self.cfgxml_data["status"].append("  </labelframe>")

        for addon_name, addon in self.addons.items():
            if hasattr(addon, "gui"):
                custom += addon.gui(self)

        # scale and offset
        for plugin_instance in self.project.plugin_instances:
            if plugin_instance.plugin_setup.get("is_joint", False) is False:
                for signal_name, signal_config in plugin_instance.signals().items():
                    halname = signal_config["halname"]
                    varname = signal_config["varname"]
                    netname = signal_config["netname"]
                    hal_type = signal_config.get("userconfig", {}).get("hal_type", signal_config.get("hal_type", "float"))
                    direction = signal_config["direction"]
                    boolean = signal_config.get("bool")
                    userconfig = signal_config.get("userconfig")
                    scale = userconfig.get("scale")
                    offset = userconfig.get("offset")
                    setp = userconfig.get("setp")
                    if not netname and setp is not None:
                        if scale:
                            self.loadrts.append(f"setp rio.{halname}-scale {scale}")
                        if offset:
                            self.loadrts.append(f"setp rio.{halname}-offset {offset}")

        # rio-functions
        self.rio_functions = {}
        for plugin_instance in self.project.plugin_instances:
            if plugin_instance.plugin_setup.get("is_joint", False) is False:
                for signal_name, signal_config in plugin_instance.signals().items():
                    halname = signal_config["halname"]
                    varname = signal_config["varname"]
                    netname = signal_config["netname"]
                    direction = signal_config["direction"]
                    boolean = signal_config.get("bool")
                    userconfig = signal_config.get("userconfig")
                    function = userconfig.get("function", "")
                    rio_function = function.split(".", 1)
                    if function and rio_function[0] in {"jog"}:
                        if rio_function[0] not in self.rio_functions:
                            self.rio_functions[rio_function[0]] = {}
                        self.rio_functions[rio_function[0]][rio_function[1]] = halname

        if "jog" in self.rio_functions:
            self.loadrts.append("")
            self.loadrts.append("# Jogging")
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
                elif function in {"position"}:
                    position_display = True
                elif function in {"wheel"}:
                    wheel = True

            if wheel:
                for axis_name, joints in self.axis_dict.items():
                    laxis = axis_name.lower()
                    self.hal_setp_add(f"axis.{laxis}.jog-vel-mode", 1)
                    self.hal_setp_add(f"axis.{laxis}.jog-scale", 0.01)
                    for joint, joint_setup in joints.items():
                        self.hal_setp_add(f"joint.{joint}.jog-vel-mode", 1)
                        self.hal_setp_add(f"joint.{joint}.jog-scale", 0.01)
                        self.hal_net_add(f"axis.{laxis}.jog-counts", f"joint.{joint}.jog-counts", f"jog-{joint}-counts")
                        self.hal_net_add(f"axisui.jog.{laxis}", f"joint.{joint}.jog-enable", f"jog-{joint}-enable")
            else:
                for axis_name, joints in self.axis_dict.items():
                    laxis = axis_name.lower()
                    fname = f"wheel_{laxis}"
                    if fname in self.rio_functions["jog"]:
                        self.hal_setp_add(f"axis.{laxis}.jog-vel-mode", 1)
                        self.hal_setp_add(f"axis.{laxis}.jog-scale", 0.01)
                        self.hal_setp_add(f"axis.{laxis}.jog-enable", 1)
                        for function, halname in self.rio_functions["jog"].items():
                            if function == fname:
                                self.hal_net_add(f"rio.{halname}-s32", f"axis.{laxis}.jog-counts", f"jog-{laxis}-counts")

                        for joint, joint_setup in joints.items():
                            self.hal_setp_add(f"joint.{joint}.jog-vel-mode", 1)
                            self.hal_setp_add(f"joint.{joint}.jog-scale", 0.01)
                            self.hal_setp_add(f"joint.{joint}.jog-enable", 1)
                            for function, halname in self.rio_functions["jog"].items():
                                if function == fname:
                                    self.hal_net_add(f"rio.{halname}-s32", f"joint.{joint}.jog-counts", f"jog-{joint}-counts")

            if speed_selector:
                self.loadrts.append("loadrt mux2 names=riof.jog.speed_mux")
                self.loadrts.append("addf riof.jog.speed_mux servo-thread")
                self.hal_setp_add("riof.jog.speed_mux.in0", 100.0)
                self.hal_setp_add("riof.jog.speed_mux.in1", 1000.0)
                for function, halname in self.rio_functions["jog"].items():
                    if function == "fast":
                        self.hal_net_add(f"rio.{halname}", "riof.jog.speed_mux.sel")
                self.hal_net_add("riof.jog.speed_mux.out", f"{prefix}.jogspeed")
                self.hal_net_add("riof.jog.speed_mux.out", "halui.axis.jog-speed")
                self.hal_net_add("riof.jog.speed_mux.out", "halui.joint.jog-speed")
                self.cfgxml_data["status"] += self.gui_gen.draw_number("Jogspeed", "jogspeed")

            if axis_move and not wheel:
                for function, halname in self.rio_functions["jog"].items():
                    if function in {"plus", "minus"}:
                        self.hal_net_add(f"rio.{halname}", f"halui.joint.selected.{function}")
                        self.hal_net_add(f"rio.{halname}", f"halui.axis.selected.{function}")

            if axis_selector:
                joint_n = 0
                for function, halname in self.rio_functions["jog"].items():
                    if function.startswith("select-"):
                        axis_name = function.split("-")[-1]
                        self.hal_net_add(f"rio.{halname}", f"halui.axis.{axis_name}.select")
                        self.hal_net_add(f"rio.{halname}", f"halui.joint.{joint_n}.select")
                        self.hal_net_add(f"halui.axis.{axis_name}.is-selected", f"{prefix}.selected-{axis_name}")
                        self.cfgxml_data["status"] += self.gui_gen.draw_led(f"Jog:{axis_name}", f"selected-{axis_name}")
                        for axis_id, joints in self.axis_dict.items():
                            laxis = axis_id.lower()
                            if axis_name == laxis:
                                self.loadrts.append("")
                                self.loadrts.append(f"# axis {laxis} selection")
                                self.loadrts.append(f"loadrt oneshot names=riof.axisui-{laxis}-oneshot")
                                self.loadrts.append(f"addf riof.axisui-{laxis}-oneshot servo-thread")
                                self.loadrts.append(f"setp riof.axisui-{laxis}-oneshot.width 0.1")
                                self.loadrts.append(f"setp riof.axisui-{laxis}-oneshot.retriggerable 0")
                                self.hal_net_add(f"axisui.jog.{laxis}", f"riof.axisui-{laxis}-oneshot.in")
                                self.hal_net_add(f"riof.axisui-{laxis}-oneshot.out", f"halui.axis.{laxis}.select")
                                for joint, joint_setup in joints.items():
                                    self.hal_net_add(f"riof.axisui-{laxis}-oneshot.out", f"halui.joint.{joint}.select")
                        joint_n += 1
            else:
                for axis_id, joints in self.axis_dict.items():
                    laxis = axis_id.lower()
                    self.loadrts.append("")
                    self.loadrts.append(f"# axis {laxis} selection")
                    self.loadrts.append(f"loadrt oneshot names=riof.axisui-{laxis}-oneshot")
                    self.loadrts.append(f"addf riof.axisui-{laxis}-oneshot servo-thread")
                    self.loadrts.append(f"setp riof.axisui-{laxis}-oneshot.width 0.1")
                    self.loadrts.append(f"setp riof.axisui-{laxis}-oneshot.retriggerable 0")
                    self.hal_net_add(f"axisui.jog.{laxis}", f"riof.axisui-{laxis}-oneshot.in")
                    self.hal_net_add(f"riof.axisui-{laxis}-oneshot.out", f"halui.axis.{laxis}.select")
                    for joint, joint_setup in joints.items():
                        self.hal_net_add(f"riof.axisui-{laxis}-oneshot.out", f"halui.joint.{joint}.select")

            if axis_selector and position_display:
                self.loadrts.append("")
                self.loadrts.append("# display position")
                self.loadrts.append("loadrt mux16 names=riof.jog.position_mux")
                self.loadrts.append("addf riof.jog.position_mux servo-thread")
                mux_select = 0
                mux_input = 1
                for function, halname in self.rio_functions["jog"].items():
                    if function.startswith("select-"):
                        axis_name = function.split("-")[-1]
                        self.hal_net_add(f"halui.axis.{axis_name}.is-selected", f"riof.jog.position_mux.sel{mux_select}")
                        self.hal_net_add(f"halui.axis.{axis_name}.pos-relative", f"riof.jog.position_mux.in{mux_input:02d}")
                        mux_select += 1
                        mux_input = mux_input * 2
                    elif function == "position":
                        self.hal_net_add(f"riof.jog.position_mux.out-f", f"rio.{halname}")

            if axis_leds:
                for function, halname in self.rio_functions["jog"].items():
                    if function.startswith("selected-"):
                        axis_name = function.split("-")[-1]
                        self.hal_net_add(f"halui.axis.{axis_name}.is-selected", f"rio.{halname}")

        for plugin_instance in self.project.plugin_instances:
            if plugin_instance.plugin_setup.get("is_joint", False) is False:
                for signal_name, signal_config in plugin_instance.signals().items():
                    halname = signal_config["halname"]
                    varname = signal_config["varname"]
                    netname = signal_config["netname"]
                    direction = signal_config["direction"]
                    userconfig = signal_config.get("userconfig", {})
                    boolean = signal_config.get("bool")
                    setp = userconfig.get("setp")
                    function = userconfig.get("function", "")
                    displayconfig = userconfig.get("display", signal_config.get("display", {}))
                    if function:
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

                    if netname or setp:
                        section = displayconfig.get("section", "status")
                        if not boolean:
                            dtype = displayconfig.get("type", "number")
                        else:
                            dtype = displayconfig.get("type", "led")
                        if dtype == "meter" and gui == "qtdragon":
                            self.hal_net_add(f"rio.{halname}", f"{prefix}.{halname}_value")
                        elif dtype != "none" and direction != "inout":
                            self.hal_net_add(f"rio.{halname}", f"{prefix}.{halname}")

                    elif direction == "input":
                        section = displayconfig.get("section", "inputs")
                        if not boolean:
                            dtype = displayconfig.get("type", "number")
                        else:
                            dtype = displayconfig.get("type", "led")

                        if dtype == "meter" and gui == "qtdragon":
                            self.hal_net_add(f"rio.{halname}", f"{prefix}.{halname}_value")
                        elif dtype != "none":
                            self.hal_net_add(f"rio.{halname}", f"{prefix}.{halname}")

                    elif direction == "output":
                        section = displayconfig.get("section", "outputs")
                        if not boolean:
                            dtype = displayconfig.get("type", "scale")
                            if dtype == "scale":
                                self.hal_net_add(f"{prefix}.{halname}-f", f"rio.{halname}")
                            elif dtype != "none":
                                self.hal_net_add(f"{prefix}.{halname}", f"rio.{halname}")

                        else:
                            dtype = displayconfig.get("type", "checkbutton")
                            if dtype != "none":
                                self.hal_net_add(f"{prefix}.{halname}", f"rio.{halname}")

                    if hasattr(self.gui_gen, f"draw_{dtype}"):
                        self.cfgxml_data[section] += getattr(self.gui_gen, f"draw_{dtype}")(halname, halname, setup=displayconfig)
                    elif dtype != "none":
                        print(f"WARNING: 'draw_{dtype}' not found")

        titles = []
        for section in self.cfgxml_data:
            if self.cfgxml_data[section]:
                titles.append(section.title())
        cfgxml_adata = []
        cfgxml_adata += self.gui_gen.draw_begin()
        cfgxml_adata += self.gui_gen.draw_tabs_begin(titles)
        for section in self.cfgxml_data:
            if self.cfgxml_data[section]:
                cfgxml_adata += self.gui_gen.draw_tab_begin(section.title())
                cfgxml_adata += self.cfgxml_data[section]
                cfgxml_adata += self.gui_gen.draw_tab_end()
        cfgxml_adata += self.gui_gen.draw_tabs_end()
        cfgxml_adata += self.gui_gen.draw_end()

        if gui == "qtdragon":
            os.system(f"mkdir -p {self.configuration_path}/rio_hd")
            os.system(f"cp -a {riocore_path}/files/rio_hd/* {self.configuration_path}/rio_hd/")
            os.system(f"cat {riocore_path}/files/rio_hd/rio_hd.ui.pre > {self.configuration_path}/rio_hd/rio_hd.ui")
            open(f"{self.configuration_path}/rio_hd/rio_hd.ui", "a").write("\n".join(cfgxml_adata))
            os.system(f"cat {riocore_path}/files/rio_hd/rio_hd.ui.post >> {self.configuration_path}/rio_hd/rio_hd.ui")
        else:
            open(f"{self.configuration_path}/rio-gui.xml", "w").write("\n".join(cfgxml_adata))

        if gui not in {"touchy", "probe_basic"}:
            self.postgui_call_list.append("custom_postgui.hal")

    def hal(self):
        linuxcnc_config = self.project.config["jdata"].get("linuxcnc", {})
        machinetype = self.project.config["jdata"].get("machinetype")

        self.loadrts.append("# load the realtime components")
        self.loadrts.append("loadrt [KINS]KINEMATICS")
        self.loadrts.append("loadrt [EMCMOT]EMCMOT base_period_nsec=[EMCMOT]BASE_PERIOD servo_period_nsec=[EMCMOT]SERVO_PERIOD num_joints=[KINS]JOINTS num_dio=[EMCMOT]NUM_DIO num_aio=[EMCMOT]NUM_AIO")
        self.loadrts.append("loadrt rio")
        self.loadrts.append("")

        num_pids = self.num_joints
        self.loadrts.append(f"loadrt pid num_chan={num_pids}")
        for pidn in range(num_pids):
            self.loadrts.append(f"addf pid.{pidn}.do-pid-calcs servo-thread")
        self.loadrts.append("")

        self.loadrts.append("# add the rio and motion functions to threads")
        self.loadrts.append("addf motion-command-handler servo-thread")
        self.loadrts.append("addf motion-controller servo-thread")
        self.loadrts.append("addf rio.readwrite servo-thread")
        self.loadrts.append("")
        self.hal_net_add("iocontrol.0.user-enable-out", "rio.sys-enable", "user-enable-out")
        self.hal_net_add("iocontrol.0.user-request-enable", "rio.sys-enable-request", "user-request-enable")

        has_estop = False
        for plugin_instance in self.project.plugin_instances:
            if plugin_instance.plugin_setup.get("is_joint", False) is False:
                for signal_name, signal_config in plugin_instance.signals().items():
                    direction = signal_config["direction"]
                    netname = signal_config["netname"]
                    if netname == "iocontrol.0.emc-enable-in" and direction == "input":
                        has_estop = True
                        break
        if not has_estop:
            self.hal_net_add("rio.sys-status", "iocontrol.0.emc-enable-in")

        self.loadrts.append("loadusr -W hal_manualtoolchange")
        self.loadrts.append("")
        self.hal_net_add("iocontrol.0.tool-prep-number", "hal_manualtoolchange.number", "tool-prep-number")
        self.hal_net_add("iocontrol.0.tool-change", "hal_manualtoolchange.change", "tool-change")
        self.hal_net_add("hal_manualtoolchange.changed", "iocontrol.0.tool-changed", "tool-changed")
        self.hal_net_add("iocontrol.0.tool-prepare", "iocontrol.0.tool-prepared", "tool-prepared")

        if machinetype == "corexy":
            self.loadrts.append("# machinetype is corexy")
            self.loadrts.append("loadrt corexy_by_hal names=corexy")
            self.loadrts.append("addf corexy servo-thread")
            self.loadrts.append("")

        for addon_name, addon in self.addons.items():
            if hasattr(addon, "hal"):
                self.loadrts += addon.hal(self)

        for plugin_instance in self.project.plugin_instances:
            if plugin_instance.plugin_setup.get("is_joint", False) is False:
                for signal_name, signal_config in plugin_instance.signals().items():
                    halname = signal_config["halname"]
                    varname = signal_config["varname"]
                    netname = signal_config["netname"]
                    userconfig = signal_config.get("userconfig", {})
                    scale = userconfig.get("scale")
                    offset = userconfig.get("offset")
                    setp = userconfig.get("setp")
                    direction = signal_config["direction"]
                    boolean = signal_config.get("bool")

                    if scale:
                        self.loadrts.append(f"setp rio.{halname}-scale {scale}")
                    if offset:
                        self.loadrts.append(f"setp rio.{halname}-offset {offset}")

                    if netname:
                        if direction == "inout":
                            self.loadrts.append(f"net rios.{halname} rio.{halname} <=> {netname}")
                        elif direction == "input":
                            net_type = halpins.LINUXCNC_SIGNALS[direction].get(netname, {}).get("type", float)
                            if net_type == int:
                                self.hal_net_add(f"rio.{halname}-s32", netname)
                            else:
                                self.hal_net_add(f"rio.{halname}", netname)
                        elif direction == "output":
                            self.hal_net_add(netname, f"rio.{halname}")
                    elif setp is not None:
                        self.loadrts.append(f"setp rio.{halname} {setp}")

        for axis_name, joints in self.axis_dict.items():
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

                    if enable_halname:
                        self.axisout.append(f"net j{joint}enable  <= joint.{joint}.amp-enable-out")
                        self.axisout.append(f"net j{joint}enable  => {enable_halname}")
                    else:
                        self.axisout.append(f"net j{joint}enable  <= joint.{joint}.amp-enable-out")
                    self.axisout.append(f"net j{joint}enable  => pid.{pin_num}.enable")
                self.axisout.append("")

    def component_variables(self):
        output = []
        output.append("// Generated by component_variables()")
        output.append("typedef struct {")
        output.append("    // hal variables")
        output.append("    hal_bit_t   *sys_enable;")
        output.append("    hal_bit_t   *sys_enable_request;")
        output.append("    hal_bit_t   *sys_status;")
        output.append("    hal_float_t *duration;")

        if self.project.multiplexed_output:
            output.append("    float MULTIPLEXER_OUTPUT_VALUE;")
            output.append("    uint8_t MULTIPLEXER_OUTPUT_ID;")
        if self.project.multiplexed_input:
            output.append("    float MULTIPLEXER_INPUT_VALUE;")
            output.append("    uint8_t MULTIPLEXER_INPUT_ID;")

        for plugin_instance in self.project.plugin_instances:
            for signal_name, signal_config in plugin_instance.signals().items():
                halname = signal_config["halname"]
                varname = signal_config["varname"]
                var_prefix = signal_config["var_prefix"]
                direction = signal_config["direction"]
                boolean = signal_config.get("bool")
                signal_source = signal_config.get("source")
                hal_type = signal_config.get("userconfig", {}).get("hal_type", signal_config.get("hal_type", "float"))
                if not boolean:
                    output.append(f"    hal_{hal_type}_t *{varname};")
                    if not signal_source and not signal_config.get("helper", False):
                        if direction == "input" and hal_type == "float":
                            output.append(f"    hal_{hal_type}_t *{varname}_ABS;")
                            output.append(f"    hal_s32_t *{varname}_S32;")
                            output.append(f"    hal_u32_t *{varname}_U32_ABS;")
                        output.append(f"    hal_float_t *{varname}_SCALE;")
                        output.append(f"    hal_float_t *{varname}_OFFSET;")
                else:
                    output.append(f"    hal_bit_t   *{varname};")
                    output.append(f"    hal_bit_t   *{varname}_not;")
                    if signal_config.get("is_index_out"):
                        output.append(f"    hal_bit_t   *{var_prefix}_INDEX_RESET;")
                        output.append(f"    hal_bit_t   *{var_prefix}_INDEX_WAIT;")

        output.append("    // raw variables")
        for size, plugin_instance, data_name, data_config in self.project.get_interface_data():
            variable_name = data_config["variable"]
            variable_size = data_config["size"]
            variable_bytesize = variable_size // 8
            if plugin_instance.TYPE == "frameio":
                output.append(f"    uint8_t {variable_name}[{variable_bytesize}];")
            elif variable_size > 1:
                output.append(f"    int{variable_size if variable_size != 24 else 32}_t {variable_name};")
            else:
                output.append(f"    bool {variable_name};")
        output.append("")
        output.append("} data_t;")
        output.append("static data_t *data;")
        output.append("")

        output.append("void register_signals(void) {")
        output.append("    int retval = 0;")

        for size, plugin_instance, data_name, data_config in self.project.get_interface_data():
            variable_name = data_config["variable"]
            variable_size = data_config["size"]
            variable_bytesize = variable_size // 8
            if plugin_instance.TYPE == "frameio":
                output.append(f"    memset(&data->{variable_name}, 0, {variable_bytesize});")
            elif variable_size > 1:
                output.append(f"    data->{variable_name} = 0;")
            else:
                output.append(f"    data->{variable_name} = 0;")
        output.append("")

        output.append('    if (retval = hal_pin_bit_newf(HAL_OUT, &(data->sys_status), comp_id, "%s.sys-status", prefix) != 0) error_handler(retval);')
        output.append('    if (retval = hal_pin_bit_newf(HAL_IN,  &(data->sys_enable), comp_id, "%s.sys-enable", prefix) != 0) error_handler(retval);')
        output.append('    if (retval = hal_pin_bit_newf(HAL_IN,  &(data->sys_enable_request), comp_id, "%s.sys-enable-request", prefix) != 0) error_handler(retval);')
        output.append('    if (retval = hal_pin_float_newf(HAL_OUT,  &(data->duration), comp_id, "%s.duration", prefix) != 0) error_handler(retval);')
        output.append("    *data->duration = rtapi_get_time();")
        for plugin_instance in self.project.plugin_instances:
            for signal_name, signal_config in plugin_instance.signals().items():
                halname = signal_config["halname"]
                direction = signal_config["direction"]
                varname = signal_config["varname"]
                var_prefix = signal_config["var_prefix"]
                boolean = signal_config.get("bool")
                hal_type = signal_config.get("userconfig", {}).get("hal_type", signal_config.get("hal_type", "float"))
                signal_source = signal_config.get("source")
                mapping = {"output": "IN", "input": "OUT", "inout": "IO"}
                hal_direction = mapping[direction]
                if not boolean:
                    if not signal_source and not signal_config.get("helper", False):
                        output.append(f'    if (retval = hal_pin_float_newf(HAL_IN, &(data->{varname}_SCALE), comp_id, "%s.{halname}-scale", prefix) != 0) error_handler(retval);')
                        output.append(f"    *data->{varname}_SCALE = 1.0;")
                        output.append(f'    if (retval = hal_pin_float_newf(HAL_IN, &(data->{varname}_OFFSET), comp_id, "%s.{halname}-offset", prefix) != 0) error_handler(retval);')
                        output.append(f"    *data->{varname}_OFFSET = 0.0;")
                    output.append(f'    if (retval = hal_pin_{hal_type}_newf(HAL_{hal_direction}, &(data->{varname}), comp_id, "%s.{halname}", prefix) != 0) error_handler(retval);')
                    output.append(f"    *data->{varname} = 0;")
                    if direction == "input" and hal_type == "float" and not signal_source and not signal_config.get("helper", False):
                        output.append(f'    if (retval = hal_pin_float_newf(HAL_{hal_direction}, &(data->{varname}_ABS), comp_id, "%s.{halname}-abs", prefix) != 0) error_handler(retval);')
                        output.append(f"    *data->{varname}_ABS = 0;")
                        output.append(f'    if (retval = hal_pin_s32_newf(HAL_{hal_direction}, &(data->{varname}_S32), comp_id, "%s.{halname}-s32", prefix) != 0) error_handler(retval);')
                        output.append(f"    *data->{varname}_S32 = 0;")
                        output.append(f'    if (retval = hal_pin_u32_newf(HAL_{hal_direction}, &(data->{varname}_U32_ABS), comp_id, "%s.{halname}-u32-abs", prefix) != 0) error_handler(retval);')
                        output.append(f"    *data->{varname}_U32_ABS = 0;")
                else:
                    output.append(f'    if (retval = hal_pin_bit_newf  (HAL_{hal_direction}, &(data->{varname}), comp_id, "%s.{halname}", prefix) != 0) error_handler(retval);')
                    output.append(f"    *data->{varname} = 0;")
                    output.append(f'    if (retval = hal_pin_bit_newf  (HAL_{hal_direction}, &(data->{varname}_not), comp_id, "%s.{halname}-not", prefix) != 0) error_handler(retval);')
                    output.append(f"    *data->{varname}_not = 1 - *data->{varname};")
                    if signal_config.get("is_index_out"):
                        output.append(
                            f'    if (retval = hal_pin_bit_newf  (HAL_{hal_direction}, &(data->{var_prefix}_INDEX_RESET), comp_id, "%s.{halname}-reset", prefix) != 0) error_handler(retval);'
                        )
                        output.append(f"    *data->{var_prefix}_INDEX_RESET = 0;")
                        output.append(f'    if (retval = hal_pin_bit_newf  (HAL_{hal_direction}, &(data->{var_prefix}_INDEX_WAIT), comp_id, "%s.{halname}-wait", prefix) != 0) error_handler(retval);')
                        output.append(f"    *data->{var_prefix}_INDEX_WAIT = 0;")

        output.append("}")
        output.append("")
        return output

    def component_signal_converter(self):
        output = []
        output.append("// Generated by component_signal_converter()")
        output.append("// output: SIGOUT -> calc -> VAROUT -> txBuffer")
        for plugin_instance in self.project.plugin_instances:
            invar = None
            for data_name, data_config in plugin_instance.interface_data().items():
                if data_config["direction"] == "input":
                    variable_name = data_config["variable"]
                    invar = variable_name

            for data_name, data_config in plugin_instance.interface_data().items():
                variable_name = data_config["variable"]
                variable_size = data_config["size"]
                variable_bytesize = variable_size // 8
                if data_config["direction"] == "output":
                    convert_parameter = []

                    if plugin_instance.TYPE == "frameio":
                        output.append(f"void convert_frame_{plugin_instance.instances_name}_output(data_t *data) {{")
                        output.append(f"    static float timeout = {plugin_instance.TIMEOUT};")
                        output.append("    static float delay = 0;")
                        output.append("    static long frame_stamp_last = 0;")
                        output.append("    static uint8_t frame_id = 0;")
                        output.append(f"    static uint8_t frame_io[{variable_bytesize}] = {{{', '.join(['0'] * variable_bytesize)}}};")
                        output.append(f"    static uint8_t frame_data[{variable_bytesize}] = {{{', '.join(['0'] * variable_bytesize)}}};")
                        output.append("    float frame_time = 0.0;")
                        output.append("    uint8_t frame_id_last = 0;")
                        output.append("    uint8_t frame_id_ack = 0;")
                        output.append("    uint8_t frame_timeout = 0;")
                        output.append("    uint8_t frame_ack = 0;")
                        output.append("    uint8_t frame_len = 0;")
                        output.append("")
                        output.append("    frame_time = (float)(stamp_last - frame_stamp_last) / 1000000.0;")
                        output.append("    if (timeout > 0 && frame_time > timeout) {")
                        output.append('        // rtapi_print("timeout: %f\\n", frame_time);')
                        output.append("        frame_timeout = 1;")
                        output.append("    }")
                        output.append("")
                        output.append(f"    frame_id_ack = data->{invar}[0];")
                        output.append("    if (frame_id_ack == frame_id) {")
                        output.append("        frame_ack = 1;")
                        output.append("    }")
                        output.append("")
                        output.append(f"    if (timeout == 0 || frame_timeout == 1 || (frame_ack == 1 && (float)(stamp_last - {plugin_instance.instances_name}_last_rx) / 1000000.0 > delay)) {{")
                        output.append("        frame_id_last = frame_id;")
                        output.append("        frame_id += 1;")

                        output.append("")
                        output.append("        /*** get plugin vars ***/")
                        output.append("")
                        for signal_name, signal_config in plugin_instance.signals().items():
                            varname = signal_config["varname"]
                            signal_values = signal_config.get("values", 1)
                            direction = signal_config["direction"]
                            boolean = signal_config.get("bool")
                            ctype = "float"
                            if boolean:
                                ctype = "bool"
                            output.append(f"        {ctype} value_{signal_name} = *data->{varname};")
                        output.append("")
                        output.append("        /***********************/")
                        output.append("")

                        output.append("        /*** plugin code ***/")
                        output.append("")
                        output.append("        " + plugin_instance.frameio_tx_c().strip())
                        output.append("")
                        output.append("        /*******************/")
                        output.append("")
                        output.append("        /*** update plugin vars ***/")
                        output.append("")
                        for signal_name, signal_config in plugin_instance.signals().items():
                            varname = signal_config["varname"]
                            signal_values = signal_config.get("values", 1)
                            direction = signal_config["direction"]
                            boolean = signal_config.get("bool")
                            output.append(f"        *data->{varname} = value_{signal_name};")
                        output.append("")
                        output.append("        /**************************/")
                        output.append("")
                        output.append("        if (frame_len > 0) {")
                        output.append("            frame_io[0] = frame_id;")
                        output.append("            frame_io[1] = frame_len;")
                        output.append("            frame_stamp_last = stamp_last;")
                        output.append(f"            memcpy(&frame_io[2], &frame_data, {variable_bytesize - 2});")
                        output.append("        }")
                        output.append("    }")
                        output.append("")
                        output.append(f"    memcpy(&data->{variable_name}, &frame_io, {variable_bytesize});")
                        output.append("}")
                        output.append("")

                    else:
                        output.append(f"void convert_{variable_name.lower()}(data_t *data){{")
                        for signal_name, signal_config in plugin_instance.signals().items():
                            varname = signal_config["varname"]
                            var_prefix = signal_config["var_prefix"]
                            boolean = signal_config.get("bool")
                            userconfig = signal_config.get("userconfig", {})
                            min_limit = userconfig.get("min_limit")
                            max_limit = userconfig.get("max_limit")

                            if data_name.upper() == varname.split("_")[-1].strip():
                                source = varname.split()[-1].strip("*")
                                if variable_size > 1:
                                    output.append(f"    float value = *data->{source};")
                                    output.append(f"    value = value * *data->{source}_SCALE;")
                                    output.append(f"    value = value + *data->{source}_OFFSET;")
                                    if min_limit is not None:
                                        output.append(f"    if (value < {min_limit}) {{")
                                        output.append(f"        value = {min_limit};")
                                        output.append("    }")
                                    if max_limit is not None:
                                        output.append(f"    if (value > {max_limit}) {{")
                                        output.append(f"        value = {max_limit};")
                                        output.append("    }")
                                    output.append("    " + plugin_instance.convert_c(data_name, data_config).strip())
                                else:
                                    output.append(f"    bool value = *data->{source};")
                                    output.append("    " + plugin_instance.convert_c(data_name, data_config).strip())
                                    if signal_config.get("is_index_enable"):
                                        output.append("    // force resetting index pin")
                                        output.append(f"    if (data->{variable_name} != value && value == 1) {{")
                                        output.append(f"        *data->{var_prefix}_INDEX_WAIT = 1;")
                                        output.append("    }")
                                        output.append(f"    if (*data->{var_prefix}_INDEX_RESET == 1) {{")
                                        output.append("       value = 0;")
                                        output.append(f"       *data->{var_prefix}_INDEX_RESET = 0;")
                                        output.append("    }")
                                output.append(f"    data->{variable_name} = value;")
                                data_config["plugin_instance"] = plugin_instance
                        output.append("}")
                        output.append("")
        output.append("")

        output.append("// input: rxBuffer -> VAROUT -> calc -> SIGOUT")
        for plugin_instance in self.project.plugin_instances:
            if plugin_instance.TYPE == "frameio":
                for data_name, data_config in plugin_instance.interface_data().items():
                    variable_name = data_config["variable"]
                    variable_size = data_config["size"]
                    variable_bytesize = variable_size // 8
                    if data_config["direction"] == "input":
                        output.append(f"void convert_frame_{plugin_instance.instances_name}_input(data_t *data) {{")
                        output.append("    static uint8_t frame_id_last = 0;")
                        output.append(f"    uint8_t frame_data[{variable_bytesize}] = {{{', '.join(['0'] * variable_bytesize)}}};")
                        output.append("    uint8_t cn = 0;")
                        output.append("    uint8_t frame_new = 0;")
                        output.append("    uint8_t frame_id = 0;")
                        output.append("    uint8_t frame_len = 0;")
                        output.append(f"    frame_id = data->{variable_name}[1];")
                        output.append(f"    frame_len = data->{variable_name}[2];")
                        output.append("    if (frame_id_last != frame_id) {")
                        output.append("        frame_id_last = frame_id;")
                        output.append("        frame_new = 1;")
                        output.append(f"        {plugin_instance.instances_name}_last_rx = stamp_last;")
                        output.append("    }")
                        output.append("    for (cn = 0; cn < frame_len; cn++) {")
                        output.append(f"        frame_data[cn] = data->{variable_name}[frame_len - cn + 2];")
                        output.append("    }")

                        output.append("")
                        output.append("    /*** get plugin vars ***/")
                        output.append("")
                        for signal_name, signal_config in plugin_instance.signals().items():
                            varname = signal_config["varname"]
                            signal_values = signal_config.get("values", 1)
                            direction = signal_config["direction"]
                            boolean = signal_config.get("bool")
                            ctype = "float"
                            if boolean:
                                ctype = "bool"
                            output.append(f"    {ctype} value_{signal_name} = *data->{varname};")
                        output.append("")
                        output.append("    /***********************/")
                        output.append("")
                        output.append("    /*** plugin code ***/")
                        output.append("")
                        output.append("    " + plugin_instance.frameio_rx_c().strip())
                        output.append("")
                        output.append("    /*******************/")
                        output.append("")

                        output.append("    /*** update plugin vars ***/")
                        output.append("")
                        for signal_name, signal_config in plugin_instance.signals().items():
                            varname = signal_config["varname"]
                            signal_values = signal_config.get("values", 1)
                            direction = signal_config["direction"]
                            boolean = signal_config.get("bool")
                            output.append(f"    *data->{varname} = value_{signal_name};")
                        output.append("")
                        output.append("    /**************************/")
                        output.append("}")
                        output.append("")
            else:
                for signal_name, signal_config in plugin_instance.signals().items():
                    varname = signal_config["varname"]
                    signal_source = signal_config.get("source")
                    signal_targets = signal_config.get("targets", {})
                    if signal_config["direction"] == "input" and not signal_source and not signal_config.get("helper", False):
                        convert_parameter = []
                        for data_name, data_config in plugin_instance.interface_data().items():
                            variable_name = data_config["variable"]
                            variable_size = data_config["size"]
                            if variable_size > 1:
                                vtype = f"int{variable_size if variable_size != 24 else 32}_t"
                                if variable_size == 8:
                                    vtype = "uint8_t"
                                convert_parameter.append(f"{vtype} *{variable_name}")
                            else:
                                convert_parameter.append(f"bool *{variable_name}")

                        direction = signal_config.get("direction")
                        boolean = signal_config.get("bool")
                        hal_type = signal_config.get("userconfig", {}).get("hal_type", signal_config.get("hal_type", "float"))

                        signal_setup = plugin_instance.plugin_setup.get("signals", {}).get(signal_name)
                        if signal_setup:
                            for signal_filter in signal_setup.get("filters", []):
                                if signal_filter.get("type") == "avg":
                                    depth = signal_filter.get("depth", 16)
                                    output.append(f"void filter_avg_{varname.lower()}(data_t *data) {{")
                                    output.append(f"    static float values[{depth}];")
                                    for parameter in convert_parameter:
                                        if signal_name.upper() == parameter.split("_")[-1].strip():
                                            source = parameter.split()[-1].strip("*")
                                            output.append(f"    float value = data->{source};")
                                            output.append("    int n = 0;")
                                            output.append("    float avg_value = 0.0;")
                                            output.append(f"    for (n = 0; n < {depth} - 1; n++) {{")
                                            output.append("        values[n] = values[n + 1];")
                                            output.append("        avg_value += values[n];")
                                            output.append("    }")
                                            output.append(f"    values[{depth-1}] = value;")
                                            output.append(f"    avg_value += values[{depth-1}];")
                                            output.append(f"    avg_value /= {depth};")
                                            output.append("")
                                            output.append(f"    data->{source} = avg_value;")

                                    output.append("}")
                                    output.append("")

                        output.append(f"void convert_{varname.lower()}(data_t *data) {{")
                        for data_name, data_config in plugin_instance.interface_data().items():
                            variable_name = data_config["variable"]
                            variable_size = data_config["size"]
                            var_prefix = signal_config["var_prefix"]
                            varname = signal_config["varname"]

                            if signal_name.upper() == variable_name.split("_")[-1].strip():
                                source = variable_name.split()[-1].strip("*")
                                if not boolean:
                                    output.append(f"    float value = data->{source};")
                                else:
                                    output.append(f"    bool value = data->{source};")

                                if signal_config.get("is_index_out"):
                                    output.append(f"    if (*data->{var_prefix}_INDEX_WAIT == 1) {{")
                                    output.append(f"        *data->{var_prefix}_INDEX_WAIT = 0;")
                                    output.append("        value = 1;")
                                    output.append("    }")
                                    output.append(f"    if (*data->{varname} != value) {{")
                                    output.append(f"        *data->{varname} = value;")
                                    output.append("        if (value == 0) {")
                                    output.append(f"            *data->SIGINOUT_{var_prefix}_INDEXENABLE = value;")
                                    output.append(f"            *data->{var_prefix}_INDEX_RESET = 1;")
                                    output.append("        }")
                                    output.append("    }")

                                convert_c = plugin_instance.convert_c(signal_name, signal_config).strip()
                                if convert_c:
                                    output.append("    " + plugin_instance.convert_c(signal_name, signal_config).strip())

                                if not boolean and direction == "input" and hal_type == "float":
                                    output.append(f"    float offset = *data->{varname}_OFFSET;")
                                    output.append(f"    float scale = *data->{varname}_SCALE;")
                                    output.append(f"    float last_value = *data->{varname};")
                                    output.append("    static float last_raw_value = 0.0;")
                                    output.append("    float raw_value = value;")
                                    output.append("    value = value + offset;")
                                    output.append("    value = value / scale;")
                                    output.append(f"    *data->{varname}_ABS = abs(value);")
                                    output.append(f"    *data->{varname}_S32 = value;")
                                    output.append(f"    *data->{varname}_U32_ABS = abs(value);")
                                output.append(f"    *data->{varname} = value;")
                                if boolean:
                                    output.append(f"    *data->{varname}_not = 1 - value;")

                                for target, calc in signal_targets.items():
                                    tvarname = f"SIGIN_{var_prefix}_{target.upper()}"
                                    output.append("")
                                    output.append(f"    // calc {target}")
                                    output.append(f"    float value_{target} = *data->{tvarname};")
                                    output.append(f"    {calc.strip()}")
                                    output.append(f"    *data->{tvarname} = value_{target};")

                                if not boolean and direction == "input" and hal_type == "float":
                                    output.append("")
                                    output.append("    last_raw_value = raw_value;")
                        output.append("}")
                        output.append("")
        output.append("")
        output.append("")
        return output

    def component_buffer_converter(self):
        output = []
        output.append("// Generated by component_buffer_converter()")
        output.append("void convert_outputs(void) {")
        output.append("    // output loop: SIGOUT -> calc -> VAROUT -> txBuffer")
        for plugin_instance in self.project.plugin_instances:
            if plugin_instance.TYPE == "frameio":
                output.append(f"    convert_frame_{plugin_instance.instances_name}_output(data);")
            else:
                for data_name, data_config in plugin_instance.interface_data().items():
                    variable_name = data_config["variable"]
                    if data_config["direction"] == "output":
                        output.append(f"    convert_{variable_name.lower()}(data);")
        output.append("}")
        output.append("")
        output.append("void convert_inputs(void) {")
        output.append("    // input: rxBuffer -> VAROUT -> calc -> SIGOUT")
        for plugin_instance in self.project.plugin_instances:
            if plugin_instance.TYPE == "frameio":
                output.append(f"    convert_frame_{plugin_instance.instances_name}_input(data);")
            else:
                for signal_name, signal_config in plugin_instance.signals().items():
                    varname = signal_config["varname"]
                    signal_source = signal_config.get("source")
                    if signal_config["direction"] == "input" and not signal_source and not signal_config.get("helper", False):
                        output.append(f"    convert_{varname.lower()}(data);")
                        signal_setup = plugin_instance.plugin_setup.get("signals", {}).get(signal_name)
                        if signal_setup:
                            for signal_filter in signal_setup.get("filters", []):
                                if signal_filter.get("type") == "avg":
                                    output.append(f"    filter_avg_{varname.lower()}(data);")

        output.append("}")
        output.append("")
        return output

    def component_buffer(self):
        output = []
        output.append("// Generated by component_buffer()")
        output.append("void write_txbuffer(uint8_t *txBuffer) {")
        output.append("    int i = 0;")
        output.append("    for (i = 0; i < BUFFER_SIZE; i++) {")
        output.append("        txBuffer[i] = 0;")
        output.append("    }")
        output.append("    // raw vars to txBuffer")
        output.append("    txBuffer[0] = 0x74;")
        output.append("    txBuffer[1] = 0x69;")
        output.append("    txBuffer[2] = 0x72;")
        output.append("    txBuffer[3] = 0x77;")

        output_pos = self.project.buffer_size - self.project.header_size

        if self.project.multiplexed_output:
            output.append("    // copy next multiplexed value")
            output.append(f"    if (data->MULTIPLEXER_OUTPUT_ID < {self.project.multiplexed_output}) {{;")
            output.append("        data->MULTIPLEXER_OUTPUT_ID += 1;")
            output.append("    } else {")
            output.append("        data->MULTIPLEXER_OUTPUT_ID = 0;")
            output.append("    };")
        mpid = 0
        for size, plugin_instance, data_name, data_config in self.project.get_interface_data():
            multiplexed = data_config.get("multiplexed", False)
            if not multiplexed:
                continue
            variable_name = data_config["variable"]
            variable_size = data_config["size"]
            if data_config["direction"] == "output":
                byte_start, byte_size, bit_offset = self.project.get_bype_pos(output_pos, variable_size)
                output.append(f"    if (data->MULTIPLEXER_OUTPUT_ID == {mpid}) {{;")
                byte_start = self.project.buffer_bytes - 1 - byte_start
                output.append(f"        memcpy(&data->MULTIPLEXER_OUTPUT_VALUE, &data->{variable_name}, {byte_size});")
                output.append("    };")
                mpid += 1

        if self.project.multiplexed_output:
            variable_size = self.project.multiplexed_output_size
            byte_start, byte_size, bit_offset = self.project.get_bype_pos(output_pos, variable_size)
            byte_start = self.project.buffer_bytes - 1 - byte_start
            output.append(f"    memcpy(&txBuffer[{byte_start-(byte_size-1)}], &data->MULTIPLEXER_OUTPUT_VALUE, {byte_size});")
            output_pos -= variable_size
            variable_size = 8
            byte_start, byte_size, bit_offset = self.project.get_bype_pos(output_pos, variable_size)
            byte_start = self.project.buffer_bytes - 1 - byte_start
            output.append(f"    memcpy(&txBuffer[{byte_start-(byte_size-1)}], &data->MULTIPLEXER_OUTPUT_ID, {byte_size});")
            output_pos -= variable_size

        for size, plugin_instance, data_name, data_config in self.project.get_interface_data():
            multiplexed = data_config.get("multiplexed", False)
            if multiplexed:
                continue
            variable_name = data_config["variable"]
            variable_size = data_config["size"]
            if data_config["direction"] == "output":
                byte_start, byte_size, bit_offset = self.project.get_bype_pos(output_pos, variable_size)
                byte_start = self.project.buffer_bytes - 1 - byte_start
                if variable_size > 1:
                    output.append(f"    memcpy(&txBuffer[{byte_start-(byte_size-1)}], &data->{variable_name}, {byte_size});")
                else:
                    output.append(f"    txBuffer[{byte_start}] |= (data->{variable_name}<<{bit_offset});")
                output_pos -= variable_size

        output.append("}")
        output.append("")
        output.append("void read_rxbuffer(uint8_t *rxBuffer) {")
        output.append("    // rxBuffer to raw vars")
        output.append("    // TODO: check rec size and header")
        input_pos = self.project.buffer_size - self.project.header_size
        if self.project.multiplexed_input:
            variable_size = self.project.multiplexed_input_size
            byte_start, byte_size, bit_offset = self.project.get_bype_pos(input_pos, variable_size)
            byte_start = self.project.buffer_bytes - 1 - byte_start
            output.append(f"    memcpy(&data->MULTIPLEXER_INPUT_VALUE, &rxBuffer[{byte_start-(byte_size-1)}], {byte_size});")
            input_pos -= variable_size
            variable_size = 8
            byte_start, byte_size, bit_offset = self.project.get_bype_pos(input_pos, variable_size)
            byte_start = self.project.buffer_bytes - 1 - byte_start
            output.append(f"    memcpy(&data->MULTIPLEXER_INPUT_ID, &rxBuffer[{byte_start-(byte_size-1)}], {byte_size});")
            input_pos -= variable_size

        for size, plugin_instance, data_name, data_config in self.project.get_interface_data():
            multiplexed = data_config.get("multiplexed", False)
            if multiplexed:
                continue
            variable_name = data_config["variable"]
            variable_size = data_config["size"]
            if data_config["direction"] == "input":
                byte_start, byte_size, bit_offset = self.project.get_bype_pos(input_pos, variable_size)
                byte_start = self.project.buffer_bytes - 1 - byte_start
                if variable_size > 1:
                    output.append(f"    memcpy(&data->{variable_name}, &rxBuffer[{byte_start-(byte_size-1)}], {byte_size});")
                else:
                    output.append(f"    data->{variable_name} = (rxBuffer[{byte_start}] & (1<<{bit_offset}));")
                input_pos -= variable_size

        mpid = 0
        for size, plugin_instance, data_name, data_config in self.project.get_interface_data():
            multiplexed = data_config.get("multiplexed", False)
            if not multiplexed:
                continue
            variable_name = data_config["variable"]
            variable_size = data_config["size"]
            if data_config["direction"] == "input":
                byte_start, byte_size, bit_offset = self.project.get_bype_pos(output_pos, variable_size)
                output.append(f"    if (data->MULTIPLEXER_INPUT_ID == {mpid}) {{;")
                byte_start = self.project.buffer_bytes - 1 - byte_start
                output.append(f"        memcpy(&data->{variable_name}, &data->MULTIPLEXER_INPUT_VALUE, {byte_size});")
                output.append("    };")
                mpid += 1

        output.append("}")
        output.append("")
        return output

    def component(self):
        output = []
        output.append("// Generated by component()")
        header_list = ["rtapi.h", "rtapi_app.h", "hal.h", "unistd.h", "stdlib.h", "stdio.h", "string.h", "math.h", "sys/mman.h"]
        if "serial":
            header_list += ["fcntl.h", "termios.h"]

        module_info = {
            "AUTHOR": "Oliver Dippel",
            "DESCRIPTION": "Driver for RIO FPGA boards",
            "LICENSE": "GPL v2",
        }

        protocol = self.project.config["jdata"].get("protocol", "SPI")

        ip = "192.168.10.194"
        port = 2390
        for plugin_instance in self.project.plugin_instances:
            if plugin_instance.TYPE == "interface":
                ip = plugin_instance.plugin_setup.get("ip", plugin_instance.option_default("ip"))
                port = plugin_instance.plugin_setup.get("port", plugin_instance.option_default("port"))

        ip = self.project.config["jdata"].get("ip", ip)
        port = self.project.config["jdata"].get("port", port)

        defines = {
            "MODNAME": '"rio"',
            "PREFIX": '"rio"',
            "JOINTS": "3",
            "BUFFER_SIZE": self.project.buffer_bytes,
            "OSC_CLOCK": self.project.config["speed"],
        }
        if port and ip:
            defines["UDP_IP"] = f'"{ip}"'
            defines["UDP_PORT"] = port
        defines["SERIAL_PORT"] = '"/dev/ttyUSB1"'
        defines["SERIAL_BAUD"] = "B1000000"

        defines["SPI_PIN_MOSI"] = "10"
        defines["SPI_PIN_MISO"] = "9"
        defines["SPI_PIN_CLK"] = "11"
        defines["SPI_PIN_CS"] = "7"
        defines["SPI_SPEED"] = "BCM2835_SPI_CLOCK_DIVIDER_256"

        for header in header_list:
            output.append(f"#include <{header}>")
        output.append("")

        for key, value in module_info.items():
            output.append(f'MODULE_{key}("{value}");')
        output.append("")

        for key, value in defines.items():
            output.append(f"#define {key} {value}")
        output.append("")

        output.append("static int 			      comp_id;")
        output.append("static const char 	      *modname = MODNAME;")
        output.append("static const char 	      *prefix = PREFIX;")
        output.append("")
        output.append("uint32_t pkg_counter = 0;")
        output.append("uint32_t err_counter = 0;")
        output.append("")
        output.append("long stamp_last = 0;")
        output.append("")
        output.append("void rio_readwrite();")
        output.append("int error_handler(int retval);")
        output.append("")

        output += self.component_variables()
        for ppath in glob.glob(f"{riocore_path}/interfaces/*/*.c"):
            if protocol == ppath.split("/")[-2]:
                output.append("/*")
                output.append(f"    interface: {os.path.basename(os.path.dirname(ppath))}")
                output.append("*/")
                output.append(open(ppath, "r").read())

        output.append("int interface_init(void) {")
        if protocol == "UART":
            output.append("    uart_init();")
        elif protocol == "SPI":
            output.append("    spi_init();")
        elif protocol == "UDP":
            output.append("    udp_init();")
        else:
            print("ERROR: unsupported interface")
            sys.exit(1)
        output.append("}")
        output.append("")

        output.append("")
        output.append("/*")
        output.append("    hal functions")
        output.append("*/")

        output.append(open(f"{riocore_path}/files/hal_functions.c", "r").read())

        output.append("")
        output.append("/***********************************************************************")
        output.append("*                         PLUGIN GLOBALS                               *")
        output.append("************************************************************************/")
        output.append("")
        for plugin_instance in self.project.plugin_instances:
            if plugin_instance.TYPE == "frameio":
                output.append(f"long {plugin_instance.instances_name}_last_rx = 0;")
            for line in plugin_instance.globals_c().strip().split("\n"):
                output.append(line)
        output.append("")
        output.append("/***********************************************************************/")
        output.append("")

        output += self.component_signal_converter()
        output += self.component_buffer_converter()
        output += self.component_buffer()
        output.append("void rio_readwrite() {")
        output.append("    uint8_t i = 0;")
        output.append("    uint8_t rxBuffer[BUFFER_SIZE * 2];")
        output.append("    uint8_t txBuffer[BUFFER_SIZE * 2];")
        output.append("    if (*data->sys_enable_request == 1) {")
        output.append("        *data->sys_status = 1;")
        output.append("    }")
        output.append("    long stamp_new = rtapi_get_time();")
        output.append("    *data->duration = (stamp_new - stamp_last) / 1000.0;")
        output.append("    stamp_last = stamp_new;")
        output.append("    if (*data->sys_enable == 1 && *data->sys_status == 1) {")
        output.append("        pkg_counter += 1;")
        output.append("        convert_outputs();")
        output.append("        write_txbuffer(txBuffer);")

        if protocol == "UART":
            output.append("        uart_trx(txBuffer, rxBuffer, BUFFER_SIZE);")
        elif protocol == "SPI":
            output.append("        spi_trx(txBuffer, rxBuffer, BUFFER_SIZE);")
        elif protocol == "UDP":
            output.append("        udp_trx(txBuffer, rxBuffer, BUFFER_SIZE);")
        else:
            print("ERROR: unsupported interface")
            sys.exit(1)

        output.append("        if (rxBuffer[0] == 97 && rxBuffer[1] == 116 && rxBuffer[2] == 97 && rxBuffer[3] == 100) {")
        output.append("            if (err_counter > 0) {")
        output.append("                err_counter = 0;")
        output.append('                rtapi_print("recovered..\\n");')
        output.append("            }")
        output.append("            read_rxbuffer(rxBuffer);")
        output.append("            convert_inputs();")
        output.append("        } else {")
        output.append("            err_counter += 1;")
        output.append('            rtapi_print("wronng header (%i): ", err_counter);')
        output.append("            for (i = 0; i < BUFFER_SIZE; i++) {")
        output.append('                rtapi_print("%d ",rxBuffer[i]);')
        output.append("            }")
        output.append('            rtapi_print("\\n");')
        output.append("            if (err_counter > 3) {")
        output.append('                rtapi_print("too much errors..\\n");')
        output.append("                *data->sys_status = 0;")
        output.append("            }")
        output.append("        }")
        output.append("    } else {")
        output.append("        *data->sys_status = 0;")
        output.append("    }")
        output.append("}")
        output.append("")
        output.append("")

        os.system(f"mkdir -p {self.component_path}/")
        open(f"{self.component_path}/rio.c", "w").write("\n".join(output))

    def create_axis_config(self):
        machinetype = self.project.config["jdata"].get("machinetype")
        pin_num = 0
        self.num_joints = 0
        self.num_axis = 0
        self.axis_dict = {}

        named_axis = []
        for plugin_instance in self.project.plugin_instances:
            if plugin_instance.plugin_setup.get("is_joint"):
                axis_name = plugin_instance.plugin_setup.get("axis")
                if axis_name:
                    named_axis.append(axis_name)

        for plugin_instance in self.project.plugin_instances:
            if plugin_instance.plugin_setup.get("is_joint"):
                axis_num = len(self.axis_dict)
                axis_name = plugin_instance.plugin_setup.get("axis")
                if not axis_name:
                    for name in self.AXIS_NAMES:
                        if name not in self.axis_dict and name not in named_axis:
                            axis_name = name
                            break
                if axis_name not in self.axis_dict:
                    self.axis_dict[axis_name] = {}
                self.axis_dict[axis_name][self.num_joints] = {
                    "type": plugin_instance.NAME,
                    "axis": axis_name,
                    "joint": self.num_joints,
                    "plugin_instance": plugin_instance,
                    "feedback": plugin_instance.plugin_setup.get("feedback", True),
                }
                self.num_joints += 1

        self.num_axis = len(self.axis_dict)

        for axis_name, joints in self.axis_dict.items():
            # print(f"  # Axis: {axis_name}")
            for joint, joint_setup in joints.items():
                position_halname = None
                enable_halname = None
                position_mode = None
                joint_config = joint_setup["plugin_instance"].plugin_setup.get("joint", {})
                position_scale = float(joint_config.get("scale", joint_setup["plugin_instance"].SIGNALS.get("position", {}).get("scale", self.JOINT_DEFAULTS["SCALE_OUT"])))
                max_velocity = float(joint_config.get("max_velocity", joint_setup["plugin_instance"].SIGNALS.get("position", {}).get("max_velocity", self.JOINT_DEFAULTS["MAX_VELOCITY"])))
                if machinetype == "lathe":
                    home_sequence_default = 2
                    if axis_name == "X":
                        home_sequence_default = 1
                else:
                    home_sequence_default = 2
                    if axis_name == "Z":
                        home_sequence_default = 1
                home_sequence = int(joint_config.get("home_sequence", home_sequence_default))
                joint_signals = joint_setup["plugin_instance"].signals()
                velocity = joint_signals.get("velocity")
                position = joint_signals.get("position")
                dty = joint_signals.get("dty")
                enable = joint_signals.get("enable")
                pos_cmd = None
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
                if position_mode == "relative" and not feedback:
                    feedback_halname = f"rio.{position['halname']}"
                    feedback_scale = position_scale
                elif position_mode == "relative":
                    fb_plugin_name, fb_signal_name = feedback.split(":")
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
                                feedback_scale = float(sub_signal_config["plugin_instance"].plugin_setup.get("scale", 320.0))
                                print("feedback", feedback, feedback_halname, feedback_scale)
                                break

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
                if position_scale < 0.0:
                    joint_setup["HOME_SEARCH_VEL"] *= -1.0
                    joint_setup["HOME_LATCH_VEL"] *= -1.0
                    joint_setup["HOME_FINAL_VEL"] *= -1.0
                    joint_setup["HOME_OFFSET"] *= -1.0

                # set autogen values
                joint_setup["SCALE_OUT"] = position_scale
                joint_setup["SCALE_IN"] = feedback_scale
                joint_setup["HOME_SEQUENCE"] = home_sequence

                # overwrite with user configuration
                for key, value in joint_config.items():
                    key = key.upper()
                    joint_setup[key] = value


class qtdragon:
    #
    # wget "https://raw.githubusercontent.com/LinuxCNC/linuxcnc/master/lib/python/qtvcp/designer/install_script"
    #

    def draw_begin(self):
        cfgxml_data = []
        cfgxml_data.append("")
        cfgxml_data.append("")
        cfgxml_data.append("           <item>")
        cfgxml_data.append('            <widget class="QGroupBox" name="groupBox_rio">')
        cfgxml_data.append('             <property name="title">')
        cfgxml_data.append("              <string>RIO</string>")
        cfgxml_data.append("             </property>")
        cfgxml_data.append('           <property name="sizePolicy">')
        cfgxml_data.append('            <sizepolicy hsizetype="Minimum" vsizetype="Preferred">')
        cfgxml_data.append("             <horstretch>0</horstretch>")
        cfgxml_data.append("             <verstretch>0</verstretch>")
        cfgxml_data.append("            </sizepolicy>")
        cfgxml_data.append("           </property>")
        cfgxml_data.append('           <property name="minimumSize">')
        cfgxml_data.append("            <size>")
        cfgxml_data.append("             <width>200</width>")
        cfgxml_data.append("             <height>0</height>")
        cfgxml_data.append("            </size>")
        cfgxml_data.append("           </property>")
        cfgxml_data.append('             <property name="alignment">')
        cfgxml_data.append("              <set>Qt::AlignCenter</set>")
        cfgxml_data.append("             </property>")
        cfgxml_data.append('             <layout class="QVBoxLayout" name="verticalLayout_30">')
        cfgxml_data.append('              <property name="spacing">')
        cfgxml_data.append("               <number>6</number>")
        cfgxml_data.append("              </property>")
        cfgxml_data.append('              <property name="leftMargin">')
        cfgxml_data.append("               <number>2</number>")
        cfgxml_data.append("              </property>")
        cfgxml_data.append('              <property name="topMargin">')
        cfgxml_data.append("               <number>2</number>")
        cfgxml_data.append("              </property>")
        cfgxml_data.append('              <property name="rightMargin">')
        cfgxml_data.append("               <number>2</number>")
        cfgxml_data.append("              </property>")
        cfgxml_data.append('              <property name="bottomMargin">')
        cfgxml_data.append("               <number>2</number>")
        cfgxml_data.append("              </property>")
        return cfgxml_data

    def draw_end(self):
        cfgxml_data = []
        cfgxml_data.append("             </layout>")
        cfgxml_data.append("            </widget>")
        cfgxml_data.append("           </item>")
        cfgxml_data.append("")
        cfgxml_data.append("")
        return cfgxml_data

    def draw_tabs_begin(self, names):
        cfgxml_data = []
        cfgxml_data.append("                    <item>")
        cfgxml_data.append('                     <widget class="QTabWidget" name="tabWidget_setup">')
        cfgxml_data.append('                      <property name="geometry">')
        cfgxml_data.append("                       <rect>")
        cfgxml_data.append("                        <x>0</x>")
        cfgxml_data.append("                        <y>0</y>")
        cfgxml_data.append("                        <width>400</width>")
        cfgxml_data.append("                        <height>300</height>")
        cfgxml_data.append("                       </rect>")
        cfgxml_data.append("                      </property>")
        cfgxml_data.append('                      <property name="sizePolicy">')
        cfgxml_data.append('                       <sizepolicy hsizetype="Expanding" vsizetype="Preferred">')
        cfgxml_data.append("                        <horstretch>1</horstretch>")
        cfgxml_data.append("                        <verstretch>0</verstretch>")
        cfgxml_data.append("                       </sizepolicy>")
        cfgxml_data.append("                      </property>")
        cfgxml_data.append('                      <property name="currentIndex">')
        cfgxml_data.append("                       <number>0</number>")
        cfgxml_data.append("                      </property>")
        return cfgxml_data

    def draw_tabs_end(self):
        cfgxml_data = []
        cfgxml_data.append("                     </widget>")
        cfgxml_data.append("                    </item>")
        return cfgxml_data

    def draw_tab_begin(self, name):
        cfgxml_data = []
        cfgxml_data.append(f'                      <widget class="QWidget" name="tab_{name}">')
        cfgxml_data.append('                       <attribute name="title">')
        cfgxml_data.append(f"                        <string>{name}</string>")
        cfgxml_data.append("                       </attribute>")
        cfgxml_data.append('                       <layout class="QVBoxLayout" name="layout_stat">')
        cfgxml_data.append('                        <property name="spacing">')
        cfgxml_data.append("                         <number>0</number>")
        cfgxml_data.append("                        </property>")
        cfgxml_data.append('                        <property name="leftMargin">')
        cfgxml_data.append("                         <number>0</number>")
        cfgxml_data.append("                        </property>")
        cfgxml_data.append('                        <property name="topMargin">')
        cfgxml_data.append("                         <number>0</number>")
        cfgxml_data.append("                        </property>")
        cfgxml_data.append('                        <property name="rightMargin">')
        cfgxml_data.append("                         <number>0</number>")
        cfgxml_data.append("                        </property>")
        cfgxml_data.append('                        <property name="bottomMargin">')
        cfgxml_data.append("                         <number>0</number>")
        cfgxml_data.append("                        </property>")
        cfgxml_data.append("                         <item>")
        cfgxml_data.append('                          <layout class="QVBoxLayout" name="verticalLayout_58">')
        return cfgxml_data

    def draw_tab_end(self):
        cfgxml_data = []
        cfgxml_data.append("                          </layout>")
        cfgxml_data.append("                         </item>")
        cfgxml_data.append("                        </layout>")
        cfgxml_data.append("                      </widget>")
        return cfgxml_data

    def draw_button(self, name, halpin, setup={}):
        return []

    def draw_scale(self, name, halpin, vmin, vmax, setup={}):
        cfgxml_data = []
        cfgxml_data.append("  <item>")
        cfgxml_data.append(f'   <layout class="QHBoxLayout" name="layl_{halpin}">')
        cfgxml_data.append("    <item>")
        cfgxml_data.append('     <widget class="QLabel" name="label_22">')
        cfgxml_data.append('      <property name="text">')
        cfgxml_data.append(f"       <string>{name}</string>")
        cfgxml_data.append("      </property>")
        cfgxml_data.append('      <property name="indent">')
        cfgxml_data.append("       <number>4</number>")
        cfgxml_data.append("      </property>")
        cfgxml_data.append("     </widget>")
        cfgxml_data.append("    </item>")
        cfgxml_data.append("    <item>")
        cfgxml_data.append(f'     <widget class="Slider" name="{halpin}">')
        cfgxml_data.append('      <property name="maximum">')
        cfgxml_data.append("       <number>100</number>")
        cfgxml_data.append("      </property>")
        cfgxml_data.append('      <property name="orientation">')
        cfgxml_data.append("       <enum>Qt::Horizontal</enum>")
        cfgxml_data.append("      </property>")
        cfgxml_data.append("     </widget>")
        cfgxml_data.append("    </item>")
        cfgxml_data.append("   </layout>")
        cfgxml_data.append("  </item>")
        return cfgxml_data

    def draw_meter(self, name, halpin, setup={}, vmin=0, vmax=100):
        display_max = setup.get("max", vmax)
        display_text = setup.get("text", name)
        display_threshold = setup.get("threshold")
        cfgxml_data = []
        cfgxml_data.append("   <item>")
        cfgxml_data.append(f'       <widget class="Gauge" name="{halpin}">')
        cfgxml_data.append('        <property name="minimumSize">')
        cfgxml_data.append("         <size>")
        cfgxml_data.append("          <width>150</width>")
        cfgxml_data.append("          <height>150</height>")
        cfgxml_data.append("         </size>")
        cfgxml_data.append("        </property>")
        cfgxml_data.append('        <property name="max_value" stdset="0">')
        cfgxml_data.append(f"         <number>{int(display_max)}</number>")
        cfgxml_data.append("        </property>")
        cfgxml_data.append('        <property name="max_reading" stdset="0">')
        cfgxml_data.append(f"         <number>{int(display_max)}</number>")
        cfgxml_data.append("        </property>")
        if display_threshold:
            cfgxml_data.append('        <property name="threshold" stdset="0">')
            cfgxml_data.append(f"         <number>{display_threshold}</number>")
            cfgxml_data.append("        </property>")
        cfgxml_data.append('        <property name="num_ticks" stdset="0">')
        cfgxml_data.append("         <number>9</number>")
        cfgxml_data.append("        </property>")
        cfgxml_data.append('        <property name="gauge_label" stdset="0">')
        cfgxml_data.append(f"         <string>{display_text}</string>")
        cfgxml_data.append("        </property>")
        cfgxml_data.append('        <property name="zone1_color" stdset="0">')
        cfgxml_data.append("         <color>")
        cfgxml_data.append("          <red>0</red>")
        cfgxml_data.append("          <green>100</green>")
        cfgxml_data.append("          <blue>0</blue>")
        cfgxml_data.append("         </color>")
        cfgxml_data.append("        </property>")
        cfgxml_data.append('        <property name="zone2_color" stdset="0">')
        cfgxml_data.append("         <color>")
        cfgxml_data.append("          <red>200</red>")
        cfgxml_data.append("          <green>0</green>")
        cfgxml_data.append("          <blue>0</blue>")
        cfgxml_data.append("         </color>")
        cfgxml_data.append("        </property>")
        cfgxml_data.append('      <property name="halpin_name" stdset="0">')
        cfgxml_data.append(f"       <string>{halpin}</string>")
        cfgxml_data.append("      </property>")
        cfgxml_data.append('      <property name="halpin_option" stdset="0">')
        cfgxml_data.append("       <bool>true</bool>")
        cfgxml_data.append("      </property>")
        cfgxml_data.append("       </widget>")
        cfgxml_data.append("   </item>")
        return cfgxml_data

    def draw_bar(self, name, halpin, setup={}, vmin=0, vmax=100):
        return self.draw_number(name, halpin, setup)

    def draw_number(self, name, halpin, hal_type="float", setup={}):
        display_format = setup.get("format", "%0.2f")
        cfgxml_data = []
        cfgxml_data.append("  <item>")
        cfgxml_data.append(f'   <layout class="QHBoxLayout" name="layl_{halpin}">')
        cfgxml_data.append("    <item>")
        cfgxml_data.append('     <widget class="QLabel" name="label_22">')
        cfgxml_data.append('      <property name="text">')
        cfgxml_data.append(f"       <string>{name}</string>")
        cfgxml_data.append("      </property>")
        cfgxml_data.append('      <property name="indent">')
        cfgxml_data.append("       <number>4</number>")
        cfgxml_data.append("      </property>")
        cfgxml_data.append("     </widget>")
        cfgxml_data.append("    </item>")
        cfgxml_data.append("    <item>")
        cfgxml_data.append(f'     <widget class="HALLabel" name="{halpin}">')
        cfgxml_data.append('      <property name="sizePolicy">')
        cfgxml_data.append('       <sizepolicy hsizetype="Minimum" vsizetype="Fixed">')
        cfgxml_data.append("        <horstretch>0</horstretch>")
        cfgxml_data.append("        <verstretch>0</verstretch>")
        cfgxml_data.append("       </sizepolicy>")
        cfgxml_data.append("      </property>")
        cfgxml_data.append('      <property name="textTemplate" stdset="0">')
        cfgxml_data.append(f"       <string>{display_format}</string>")
        cfgxml_data.append("      </property>")
        cfgxml_data.append('      <property name="styleSheet">')
        cfgxml_data.append('       <string notr="true">font: 20pt &quot;Lato Heavy&quot;;</string>')
        cfgxml_data.append("      </property>")
        cfgxml_data.append('      <property name="bit_pin_type" stdset="0">')
        cfgxml_data.append("       <bool>false</bool>")
        cfgxml_data.append("      </property>")
        cfgxml_data.append('      <property name="float_pin_type" stdset="0">')
        cfgxml_data.append("       <bool>true</bool>")
        cfgxml_data.append("      </property>")
        cfgxml_data.append("     </widget>")
        cfgxml_data.append("    </item>")
        cfgxml_data.append("   </layout>")
        cfgxml_data.append("  </item>")
        return cfgxml_data

    def draw_checkbutton(self, name, halpin, setup={}):
        cfgxml_data = []
        cfgxml_data.append("  <item>")
        cfgxml_data.append(f'   <layout class="QHBoxLayout" name="layl_{halpin}">')
        cfgxml_data.append("    <item>")
        cfgxml_data.append(f'     <widget class="PushButton" name="{halpin}">')
        cfgxml_data.append('      <property name="text">')
        cfgxml_data.append(f"       <string>{name}</string>")
        cfgxml_data.append("      </property>")
        cfgxml_data.append('      <property name="checkable">')
        cfgxml_data.append("        <bool>true</bool>")
        cfgxml_data.append("      </property>")
        cfgxml_data.append('      <property name="styleSheet">')
        cfgxml_data.append('        <string notr="true">font: 18pt &quot;Lato Heavy&quot;;</string>')
        cfgxml_data.append("      </property>")
        cfgxml_data.append('      <property name="minimumSize">')
        cfgxml_data.append("        <size>")
        cfgxml_data.append("         <width>32</width>")
        cfgxml_data.append("         <height>32</height>")
        cfgxml_data.append("        </size>")
        cfgxml_data.append("      </property>")
        cfgxml_data.append("     </widget>")
        cfgxml_data.append("    </item>")
        cfgxml_data.append("   </layout>")
        cfgxml_data.append("  </item>")
        return cfgxml_data

    def draw_led(self, name, halpin, setup={}):
        cfgxml_data = []
        cfgxml_data.append("  <item>")
        cfgxml_data.append(f'   <layout class="QHBoxLayout" name="layl_{halpin}">')
        cfgxml_data.append("    <item>")
        cfgxml_data.append('     <widget class="QLabel" name="label_22">')
        cfgxml_data.append('      <property name="text">')
        cfgxml_data.append(f"       <string>{name}</string>")
        cfgxml_data.append("      </property>")
        cfgxml_data.append('      <property name="indent">')
        cfgxml_data.append("       <number>4</number>")
        cfgxml_data.append("      </property>")
        cfgxml_data.append("     </widget>")
        cfgxml_data.append("    </item>")
        cfgxml_data.append("    <item>")
        cfgxml_data.append(f'     <widget class="LED" name="{halpin}">')
        cfgxml_data.append('        <property name="sizePolicy">')
        cfgxml_data.append('         <sizepolicy hsizetype="Fixed" vsizetype="Fixed">')
        cfgxml_data.append("          <horstretch>0</horstretch>")
        cfgxml_data.append("          <verstretch>0</verstretch>")
        cfgxml_data.append("         </sizepolicy>")
        cfgxml_data.append("        </property>")
        cfgxml_data.append('        <property name="minimumSize">')
        cfgxml_data.append("         <size>")
        cfgxml_data.append("          <width>32</width>")
        cfgxml_data.append("          <height>32</height>")
        cfgxml_data.append("         </size>")
        cfgxml_data.append("        </property>")
        cfgxml_data.append('        <property name="color">')
        cfgxml_data.append("          <color>")
        if halpin.endswith(".B"):
            cfgxml_data.append("           <red>85</red>")
            cfgxml_data.append("           <green>0</green>")
            cfgxml_data.append("           <blue>255</blue>")
        elif halpin.endswith(".R"):
            cfgxml_data.append("           <red>255</red>")
            cfgxml_data.append("           <green>85</green>")
            cfgxml_data.append("           <blue>0</blue>")
        else:
            cfgxml_data.append("           <red>85</red>")
            cfgxml_data.append("           <green>255</green>")
            cfgxml_data.append("           <blue>0</blue>")

        cfgxml_data.append("          </color>")
        cfgxml_data.append("        </property>")
        cfgxml_data.append('        <property name="maximumSize">')
        cfgxml_data.append("         <size>")
        cfgxml_data.append("          <width>32</width>")
        cfgxml_data.append("          <height>32</height>")
        cfgxml_data.append("         </size>")
        cfgxml_data.append("        </property>")
        cfgxml_data.append("     </widget>")
        cfgxml_data.append("    </item>")
        cfgxml_data.append("   </layout>")
        cfgxml_data.append("  </item>")
        return cfgxml_data


class axis:
    def draw_begin(self):
        cfgxml_data = []
        cfgxml_data.append("<pyvcp>")
        return cfgxml_data

    def draw_end(self):
        cfgxml_data = []
        cfgxml_data.append('<label><text>""</text><width>30</width></label>')
        cfgxml_data.append("</pyvcp>")
        return cfgxml_data

    def draw_tabs_begin(self, names):
        cfgxml_data = []
        cfgxml_data.append("<tabs>")
        cfgxml_data.append(f"    <names>{names}</names>")
        return cfgxml_data

    def draw_tabs_end(self):
        cfgxml_data = []
        cfgxml_data.append("</tabs>")
        return cfgxml_data

    def draw_tab_begin(self, name):
        cfgxml_data = []
        cfgxml_data.append("    <vbox>")
        return cfgxml_data

    def draw_tab_end(self):
        cfgxml_data = []
        cfgxml_data.append("    </vbox>")
        return cfgxml_data

    def draw_scale(self, name, halpin, setup={}, vmin=0, vmax=100):
        title = setup.get("title", name)
        display_min = setup.get("min", vmin)
        display_max = setup.get("max", vmax)
        resolution = setup.get("resolution", 0.1)
        cfgxml_data = []
        cfgxml_data.append("  <hbox>")
        cfgxml_data.append("    <relief>RAISED</relief>")
        cfgxml_data.append("    <bd>2</bd>")
        cfgxml_data.append("    <scale>")
        cfgxml_data.append(f'      <halpin>"{halpin}"</halpin>')
        cfgxml_data.append(f"      <resolution>{resolution}</resolution>")
        cfgxml_data.append("      <orient>HORIZONTAL</orient>")
        cfgxml_data.append("      <initval>0</initval>")
        cfgxml_data.append(f"      <min_>{display_min}</min_>")
        cfgxml_data.append(f"      <max_>{display_max}</max_>")
        cfgxml_data.append("      <param_pin>1</param_pin>")
        cfgxml_data.append("    </scale>")
        cfgxml_data.append("    <label>")
        cfgxml_data.append(f'      <text>"{title}"</text>')
        cfgxml_data.append("    </label>")
        cfgxml_data.append("  </hbox>")
        return cfgxml_data

    def draw_spinbox(self, name, halpin, setup={}, vmin=0, vmax=100):
        title = setup.get("title", name)
        display_min = setup.get("min", vmin)
        display_max = setup.get("max", vmax)
        resolution = setup.get("resolution", 0.1)
        cfgxml_data = []
        cfgxml_data.append("  <hbox>")
        cfgxml_data.append("    <relief>RAISED</relief>")
        cfgxml_data.append("    <bd>2</bd>")
        cfgxml_data.append("    <spinbox>")
        cfgxml_data.append(f'      <halpin>"{halpin}"</halpin>')
        cfgxml_data.append(f"      <resolution>{resolution}</resolution>")
        cfgxml_data.append("      <initval>0</initval>")
        cfgxml_data.append(f"      <min_>{display_min}</min_>")
        cfgxml_data.append(f"      <max_>{display_max}</max_>")
        cfgxml_data.append("      <param_pin>1</param_pin>")
        cfgxml_data.append("    </spinbox>")
        cfgxml_data.append("    <label>")
        cfgxml_data.append(f'      <text>"{title}"</text>')
        cfgxml_data.append("    </label>")
        cfgxml_data.append("  </hbox>")
        return cfgxml_data

    def draw_jogwheel(self, name, halpin, setup={}, vmin=0, vmax=100):
        title = setup.get("title", name)
        display_min = setup.get("min", vmin)
        display_max = setup.get("max", vmax)
        resolution = setup.get("resolution", 0.1)
        size = setup.get("size", 200)
        cpr = setup.get("cpr", 50)
        cfgxml_data = []
        cfgxml_data.append("    <jogwheel>")
        cfgxml_data.append(f'      <halpin>"{halpin}"</halpin>')
        cfgxml_data.append(f'      <text>"{title}"</text>')
        cfgxml_data.append(f"      <size>{size}</size>")
        cfgxml_data.append(f"      <cpr>{cpr}</cpr>")
        cfgxml_data.append(f"      <resolution>{resolution}</resolution>")
        cfgxml_data.append("      <initval>0</initval>")
        cfgxml_data.append(f"      <min_>{display_min}</min_>")
        cfgxml_data.append(f"      <max_>{display_max}</max_>")
        cfgxml_data.append("      <param_pin>1</param_pin>")
        cfgxml_data.append("    </jogwheel>")
        return cfgxml_data

    def draw_dial(self, name, halpin, setup={}, vmin=0, vmax=100):
        title = setup.get("title", name)
        display_min = setup.get("min", vmin)
        display_max = setup.get("max", vmax)
        resolution = setup.get("resolution", 0.1)
        dialcolor = setup.get("dialcolor", "yellow")
        edgecolor = setup.get("edgecolor", "green")
        dotcolor = setup.get("dotcolor", "black")
        size = setup.get("size", 200)
        cpr = setup.get("cpr", 50)
        cfgxml_data = []
        cfgxml_data.append("    <dial>")
        cfgxml_data.append(f'      <halpin>"{halpin}"</halpin>')
        cfgxml_data.append(f'      <text>"{title}"</text>')
        cfgxml_data.append(f"      <size>{size}</size>")
        cfgxml_data.append(f"      <cpr>{cpr}</cpr>")
        cfgxml_data.append(f"      <resolution>{resolution}</resolution>")
        cfgxml_data.append(f'      <dialcolor>"{dialcolor}"</dialcolor>')
        cfgxml_data.append(f'      <edgecolor>"{edgecolor}"</edgecolor>')
        cfgxml_data.append(f'      <dotcolor>"{dotcolor}"</dotcolor>')
        cfgxml_data.append("      <initval>0</initval>")
        cfgxml_data.append(f"      <min_>{display_min}</min_>")
        cfgxml_data.append(f"      <max_>{display_max}</max_>")
        cfgxml_data.append("      <param_pin>1</param_pin>")
        cfgxml_data.append("    </dial>")
        return cfgxml_data

    def draw_meter(self, name, halpin, setup={}, vmin=0, vmax=100):
        title = setup.get("title", name)
        display_min = setup.get("min", vmin)
        display_max = setup.get("max", vmax)
        display_subtext = setup.get("subtext", "")
        display_region = setup.get("region", [])
        display_size = setup.get("size", 150)
        cfgxml_data = []
        cfgxml_data.append("  <hbox>")
        cfgxml_data.append("    <relief>RAISED</relief>")
        cfgxml_data.append("    <bd>2</bd>")
        cfgxml_data.append("  <meter>")
        cfgxml_data.append(f'      <halpin>"{halpin}"</halpin>')
        cfgxml_data.append(f'      <text>"{title}"</text>')
        cfgxml_data.append(f'      <subtext>"{display_subtext}"</subtext>')
        cfgxml_data.append(f"      <size>{display_size}</size>")
        cfgxml_data.append(f"      <min_>{display_min}</min_>")
        cfgxml_data.append(f"      <max_>{display_max}</max_>")
        for rnum, region in enumerate(display_region):
            cfgxml_data.append(f'      <region{rnum + 1}>({region[0]},{region[1]},"{region[2]}")</region{rnum + 1}>')
        cfgxml_data.append("    </meter>")
        cfgxml_data.append("  </hbox>")
        return cfgxml_data

    def draw_bar(self, name, halpin, setup={}, vmin=0, vmax=100):
        title = setup.get("title", name)
        display_min = setup.get("min", vmin)
        display_max = setup.get("max", vmax)
        display_range = setup.get("range", [])
        display_format = setup.get("format", "05d")
        display_fillcolor = setup.get("fillcolor", "red")
        display_bgcolor = setup.get("fillcolor", "grey")
        cfgxml_data = []
        cfgxml_data.append("  <hbox>")
        cfgxml_data.append("    <relief>RAISED</relief>")
        cfgxml_data.append("    <bd>2</bd>")
        cfgxml_data.append("    <label>")
        cfgxml_data.append(f'      <text>"{title}"</text>')
        cfgxml_data.append("    </label>")
        cfgxml_data.append("    <bar>")
        cfgxml_data.append(f'    <halpin>"{halpin}"</halpin>')
        cfgxml_data.append(f"    <min_>{display_min}</min_>")
        cfgxml_data.append(f"    <max_>{display_max}</max_>")
        cfgxml_data.append(f'    <format>"{display_format}"</format>')
        cfgxml_data.append(f'    <bgcolor>"{display_bgcolor}"</bgcolor>')
        cfgxml_data.append(f'    <fillcolor>"{display_fillcolor}"</fillcolor>')
        for rnum, brange in enumerate(display_range):
            cfgxml_data.append(f'    <range{rnum + 1}>({brange[0]},{brange[1]},"{brange[2]}")</range{rnum + 1}>')
        cfgxml_data.append("    </bar>")
        cfgxml_data.append("  </hbox>")
        return cfgxml_data

    def draw_number(self, name, halpin, hal_type="float", setup={}):
        title = setup.get("title", name)
        display_format = setup.get("format")
        unit = setup.get("unit")
        element = "number"
        if not display_format:
            if hal_type != "float":
                display_format = "d"
                element = hal_type
            else:
                display_format = "07.2f"
        cfgxml_data = []
        cfgxml_data.append("  <hbox>")
        cfgxml_data.append("    <relief>RAISED</relief>")
        cfgxml_data.append("    <bd>2</bd>")
        cfgxml_data.append("    <label>")
        cfgxml_data.append(f'      <text>"{title:10s}"</text>')
        cfgxml_data.append('      <font>("Helvetica",9)</font>')
        cfgxml_data.append("      <width>13</width>")
        cfgxml_data.append("    </label>")
        cfgxml_data.append(f"    <{element}>")
        cfgxml_data.append(f'        <halpin>"{halpin}"</halpin>')
        cfgxml_data.append('        <font>("Helvetica",14)</font>')
        cfgxml_data.append(f'        <format>"{display_format}"</format>')
        # cfgxml_data.append(f'        <width>13</width>')
        cfgxml_data.append("      <justify>LEFT</justify>")
        cfgxml_data.append(f"    </{element}>")
        if unit:
            cfgxml_data.append("    <label>")
            cfgxml_data.append('        <font>("Helvetica",14)</font>')
            cfgxml_data.append(f'      <text>"{unit}"</text>')
            cfgxml_data.append("    </label>")
        cfgxml_data.append("  </hbox>")
        return cfgxml_data

    def draw_checkbutton(self, name, halpin, setup={}):
        title = setup.get("title", name)
        cfgxml_data = []
        cfgxml_data.append("  <hbox>")
        cfgxml_data.append("    <relief>RAISED</relief>")
        cfgxml_data.append("    <bd>2</bd>")
        cfgxml_data.append("    <label>")
        cfgxml_data.append(f'      <text>"{title:10s}"</text>')
        cfgxml_data.append('      <font>("Helvetica",9)</font>')
        cfgxml_data.append("      <width>13</width>")
        cfgxml_data.append("    </label>")
        cfgxml_data.append("    <checkbutton>")
        cfgxml_data.append(f'      <halpin>"{halpin}"</halpin>')
        # cfgxml_data.append(f'      <text>"{title}"</text>')
        cfgxml_data.append("    </checkbutton>")
        cfgxml_data.append("  </hbox>")
        return cfgxml_data

    def draw_checkbutton_rgb(self, name, halpin_g, halpin_b, halpin_r, setup={}):
        title = setup.get("title", name)
        cfgxml_data = []
        cfgxml_data.append("  <hbox>")
        cfgxml_data.append("    <relief>RAISED</relief>")
        cfgxml_data.append("    <bd>2</bd>")
        cfgxml_data.append("    <label>")
        cfgxml_data.append(f'      <text>"{title}"</text>')
        cfgxml_data.append("    </label>")
        cfgxml_data.append("    <checkbutton>")
        cfgxml_data.append(f'      <halpin>"{halpin_g}"</halpin>')
        cfgxml_data.append('      <text>"G"</text>')
        cfgxml_data.append("    </checkbutton>")
        cfgxml_data.append("    <checkbutton>")
        cfgxml_data.append(f'      <halpin>"{halpin_b}"</halpin>')
        cfgxml_data.append('      <text>"B"</text>')
        cfgxml_data.append("    </checkbutton>")
        cfgxml_data.append("    <checkbutton>")
        cfgxml_data.append(f'      <halpin>"{halpin_r}"</halpin>')
        cfgxml_data.append('      <text>"R"</text>')
        cfgxml_data.append("    </checkbutton>")
        cfgxml_data.append("  </hbox>")
        return cfgxml_data

    def draw_led(self, name, halpin, setup={}):
        title = setup.get("title", name)
        size = setup.get("size", 16)
        color = setup.get("color")
        cfgxml_data = []
        cfgxml_data.append("  <hbox>")
        cfgxml_data.append("    <relief>RAISED</relief>")
        cfgxml_data.append("    <bd>2</bd>")
        cfgxml_data.append("    <label>")
        cfgxml_data.append(f'      <text>"{title:10s}"</text>')
        cfgxml_data.append('      <font>("Helvetica",9)</font>')
        cfgxml_data.append("      <width>13</width>")
        cfgxml_data.append("    </label>")
        cfgxml_data.append("    <led>")
        cfgxml_data.append(f'      <halpin>"{halpin}"</halpin>')
        cfgxml_data.append(f"      <size>{size}</size>")
        if color:
            cfgxml_data.append(f'      <on_color>"{color}"</on_color>')
        elif halpin.endswith(".R"):
            cfgxml_data.append('      <on_color>"red"</on_color>')
        elif halpin.endswith(".B"):
            cfgxml_data.append('      <on_color>"blue"</on_color>')
        else:
            cfgxml_data.append('      <on_color>"green"</on_color>')
        cfgxml_data.append('      <off_color>"black"</off_color>')
        cfgxml_data.append("    </led>")
        cfgxml_data.append("  </hbox>")
        return cfgxml_data

    def draw_rectled(self, name, halpin, setup={}):
        title = setup.get("title", name)
        width = setup.get("width", 16)
        height = setup.get("height", 16)
        color = setup.get("color")
        cfgxml_data = []
        cfgxml_data.append("  <hbox>")
        cfgxml_data.append("    <relief>RAISED</relief>")
        cfgxml_data.append("    <bd>2</bd>")
        cfgxml_data.append("    <label>")
        cfgxml_data.append(f'      <text>"{title:10s}"</text>')
        cfgxml_data.append('      <font>("Helvetica",9)</font>')
        cfgxml_data.append("      <width>13</width>")
        cfgxml_data.append("    </label>")
        cfgxml_data.append("    <led>")
        cfgxml_data.append(f'      <halpin>"{halpin}"</halpin>')
        cfgxml_data.append(f"      <width>{width}</width>")
        cfgxml_data.append(f"      <height>{height}</height>")
        if color:
            cfgxml_data.append(f'      <on_color>"{color}"</on_color>')
        elif halpin.endswith(".R"):
            cfgxml_data.append('      <on_color>"red"</on_color>')
        elif halpin.endswith(".B"):
            cfgxml_data.append('      <on_color>"blue"</on_color>')
        else:
            cfgxml_data.append('      <on_color>"green"</on_color>')
        cfgxml_data.append('      <off_color>"black"</off_color>')
        cfgxml_data.append("    </led>")
        cfgxml_data.append("  </hbox>")
        return cfgxml_data

    def draw_button(self, name, halpin, setup={}):
        title = setup.get("title", name)
        cfgxml_data = []
        cfgxml_data.append("  <button>")
        cfgxml_data.append("    <relief>RAISED</relief>")
        cfgxml_data.append("    <bd>3</bd>")
        cfgxml_data.append(f'    <halpin>"{halpin}"</halpin><text>"{title}"</text>')
        cfgxml_data.append('    <font>("Helvetica", 12)</font>')
        cfgxml_data.append("  </button>")
        return cfgxml_data
