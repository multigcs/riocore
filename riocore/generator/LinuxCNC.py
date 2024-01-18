import glob
import os

riocore_path = os.path.dirname(os.path.dirname(__file__))

class LinuxCNC:
    AXIS_NAMES = ["X", "Y", "Z", "A", "C", "B", "U", "V", "W"]

    def __init__(self, project):
        self.used_signals = {}
        self.project = project
        self.base_path = f"{self.project.config['output_path']}/LinuxCNC"
        self.component_path = f"{self.base_path}/Component"
        self.configuration_path = f"{self.base_path}/Configuration"
        self.create_axis_config()

    def generator(self):
        self.component()
        self.ini()
        self.hal()
        self.gui()
        self.misc()
        print(f"writing linuxcnc files to: {self.base_path}")

    def ini(self):

        AXIS_DEFAULTS = {
            "MAX_VELOCITY": 40.0,
            "MAX_ACCELERATION": 500.0,
            "MIN_LIMIT": -150,
            "MAX_LIMIT": 150,
            "MIN_FERROR": 0.01,
            "FERROR": 1.0,
        }
        PID_DEFAULTS = {
            "P": 50.0,
            "I": 0.0,
            "D": 0.0,
            "BIAS": 0.0,
            "FF0": 0.0,
            "FF1": 0.0,
            "FF2": 0.0,
            "DEADBAND": 0,
            "MAXOUTPUT": 300,
        }
        JOINT_DEFAULTS = {
            "TYPE": "LINEAR",
            "HOME": 0.0,
            "MIN_LIMIT": -200.0,
            "MAX_LIMIT": 150.0,
            "MAX_VELOCITY": 40.0,
            "MAX_ACCELERATION": 500.0,
            "STEPGEN_MAXACCEL": 2000.0,
            "SCALE_OUT": 1600.0,
            "SCALE_IN": 1600.0,
            "HOME_SEARCH_VEL": 20.0,
            "HOME_LATCH_VEL": 3.0,
            "HOME_FINAL_VEL": -20,
            "HOME_IGNORE_LIMITS": "YES",
            "HOME_USE_INDEX": "NO",
            "HOME_OFFSET": 6.5,
            "HOME": 0.0,
            "HOME_SEQUENCE": 3,
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
                "MIN_SPINDLE_0_OVERRIDE": 0.5,
                "MAX_SPINDLE_0_OVERRIDE": 1.2,
                "MIN_SPINDLE_0_SPEED": 1000,
                "DEFAULT_SPINDLE_0_SPEED": 6000,
                "MAX_SPINDLE_0_SPEED": 20000,
                "MIN_LINEAR_VELOCITY": 0.0,
                "DEFAULT_LINEAR_VELOCITY": 40.0,
                "MAX_LINEAR_VELOCITY": 80.0,
                "MIN_ANGULAR_VELOCITY": 0.0,
                "DEFAULT_ANGULAR_VELOCITY": 2.5,
                "MAX_ANGULAR_VELOCITY": 5.0,
                "SPINDLE_INCREMENT": 200,
                "MAX_SPINDLE_POWER": 2000,
            },
            "KINS": {
                "JOINTS": None,
                "KINEMATICS": None,
            },
            "FILTER": {
                "PROGRAM_EXTENSION": [
                    ".ngc,.nc,.tap G-Code File (*.ngc,*.nc,*.tap)",
                    ".py Python Script",
                ],
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
                "HALFILE": "rio.hal",
                "POSTGUI_HALFILE": "postgui_call_list.hal",
                "HALUI": "halui",
            },
            "HALUI": {
                "MDI_COMMAND": [
                    "G92 X0 Y0",
                    "G92 Z0",
                    "o<z_touch> call",
                ],
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

        ini_setup = INI_DEFAULTS.copy()

        coordinates = []
        for axis_name, joints in self.axis_dict.items():
            for joint, joint_setup in joints.items():
                coordinates.append(axis_name)

        kinematics = "trivkins"
        ini_setup["KINS"]["JOINTS"] = self.num_joints
        ini_setup["KINS"]["KINEMATICS"] = f"{kinematics} coordinates={''.join(coordinates)}"
        ini_setup["TRAJ"]["COORDINATES"] = "".join(coordinates)
        ini_setup["EMCMOT"]["NUM_DIO"] = 3
        ini_setup["EMCMOT"]["NUM_AIO"] = 3

        output = []
        for section, setup in ini_setup.items():
            output.append(f"[{section}]")
            for key, value in setup.items():
                if isinstance(value, list):
                    for entry in value:
                        output.append(f"{key} = {entry}")
                elif value is not None:
                    output.append(f"{key} = {value}")
            output.append("")

        for axis_name, joints in self.axis_dict.items():
            output.append(f"[AXIS_{axis_name}]")
            for key, value in AXIS_DEFAULTS.items():
                output.append(f"{key:18s} = {value}")
            output.append("")
            for joint, joint_setup in joints.items():
                position_mode = joint_setup["position_mode"]
                position_halname = joint_setup["position_halname"]
                feedback_halname = joint_setup["feedback_halname"]
                enable_halname = joint_setup["enable_halname"]
                position_scale = joint_setup["position_scale"]
                feedback_scale = joint_setup["feedback_scale"]
                pin_num = joint_setup["pin_num"]
                joint_setup = JOINT_DEFAULTS.copy()

                # TODO: set scales
                joint_setup["SCALE_OUT"] = position_scale
                joint_setup["SCALE_IN"] = feedback_scale

                output.append(f"[JOINT_{joint}]")
                if position_mode == "absolute":
                    for key, value in joint_setup.items():
                        output.append(f"{key:18s} = {value}")

                elif position_halname and feedback_halname:
                    pid_setup = PID_DEFAULTS.copy()
                    for key, value in pid_setup.items():
                        output.append(f"{key:18s} = {value}")
                    output.append("")
                    for key, value in joint_setup.items():
                        output.append(f"{key:18s} = {value}")
                output.append("")

        os.system(f"mkdir -p {self.configuration_path}/")
        open(f"{self.configuration_path}/rio.ini", "w").write("\n".join(output))

    def misc(self):
        tooltbl = []
        tooltbl.append("T1 P1 D0.125000 Z+0.511000 ;1/8 end mill")
        tooltbl.append("T2 P2 D0.062500 Z+0.100000 ;1/16 end mill")
        tooltbl.append("T3 P3 D0.201000 Z+1.273000 ;#7 tap drill")
        # TODO: do not overwrite existing
        os.system(f"mkdir -p {self.configuration_path}/")
        open(f"{self.configuration_path}/tool.tbl", "w").write("\n".join(tooltbl))

    def gui(self):
        os.system(f"mkdir -p {self.configuration_path}/")
        gui_gen = axis()
        custom = []
        cfgxml_data_status = []
        cfgxml_data_inputs = []
        cfgxml_data_outputs = []

        # scale and offset
        for plugin_instance in self.project.plugin_instances:
            if plugin_instance.plugin_setup.get("joint", False) is False:
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
                    if scale:
                        custom.append(f"setp rio.{halname}-scale {scale}")
                    if offset:
                        custom.append(f"setp rio.{halname}-offset {offset}")

        # rio-functions
        self.rio_functions = {}
        for plugin_instance in self.project.plugin_instances:
            if plugin_instance.plugin_setup.get("joint", False) is False:
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
            custom.append("# Jogging")
            speed_selector = False
            axis_selector = False
            axis_leds = False
            axis_move = False
            position_display = False
            for function, halname in self.rio_functions["jog"].items():
                self.used_signals[halname] = f"riof.jog.{function}"
                custom.append(f"net {self.used_signals[halname]:16s} <= rio.{halname}")
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

            if speed_selector:
                custom.append("loadrt mux2 names=riof.jog.speed_mux")
                custom.append("addf riof.jog.speed_mux servo-thread")
                custom.append("setp riof.jog.speed_mux.in0 100.0")
                custom.append("setp riof.jog.speed_mux.in1 1000.0")
                custom.append("net riof.jog.fast => riof.jog.speed_mux.sel")
                custom.append("net riof.jog.speed <= riof.jog.speed_mux.out")
                custom.append(f"net riof.jog.speed => pyvcp.jogspeed")
                cfgxml_data_status += gui_gen.draw_number("Jogspeed", "jogspeed")
            else:
                custom.append("setp riof.jog.speed 500")
            custom.append("net riof.jog.speed => halui.axis.jog-speed")
            custom.append("net riof.jog.speed => halui.joint.jog-speed")
            custom.append("")
            if axis_move:
                custom.append("net riof.jog.minus => halui.joint.selected.minus")
                custom.append("net riof.jog.minus => halui.axis.selected.minus")
                custom.append("net riof.jog.plus  => halui.joint.selected.plus")
                custom.append("net riof.jog.plus  => halui.axis.selected.plus")
                custom.append("")
            if axis_selector:
                joint_n = 0
                for function, halname in self.rio_functions["jog"].items():
                    if function.startswith("select-"):
                        axis_name = function.split("-")[-1]
                        custom.append(f"net riof.jog.{function} => halui.axis.{axis_name}.select")
                        custom.append(f"net riof.jog.{function} => halui.joint.{joint_n}.select")
                        custom.append(f"net riof.jog.selected-{axis_name} => pyvcp.{halname}")
                        cfgxml_data_status += gui_gen.draw_led(f"Jog:{axis_name}", halname)
                        joint_n += 1

            if axis_selector and position_display:
                custom.append("# display position")
                custom.append(f"loadrt mux16 names=riof.jog.position_mux")
                custom.append(f"addf riof.jog.position_mux servo-thread")
                custom.append(f"net riof.jog.position <= riof.jog.position_mux.out-f")
                mux_select = 0
                mux_input = 1
                for function, halname in self.rio_functions["jog"].items():
                    if function.startswith("select-"):
                        axis_name = function.split("-")[-1]
                        custom.append(f"net riof.jog.selected-{axis_name} => riof.jog.position_mux.sel{mux_select}")
                        custom.append(f"net riof.jog.pos-{axis_name} halui.axis.{axis_name}.pos-feedback => riof.jog.position_mux.in{mux_input:02d}")
                        mux_select += 1
                        mux_input = mux_input * 2

                custom.append("")
            if axis_leds:
                for function, halname in self.rio_functions["jog"].items():
                    if function.startswith("selected-"):
                        axis_name = function.split("-")[-1]
                        custom.append(f"net riof.jog.{function} <= halui.axis.{axis_name}.is-selected")
                custom.append("")

        for plugin_instance in self.project.plugin_instances:
            if plugin_instance.plugin_setup.get("joint", False) is False:
                for signal_name, signal_config in plugin_instance.signals().items():
                    halname = signal_config["halname"]
                    varname = signal_config["varname"]
                    netname = signal_config["netname"]
                    hal_type = signal_config.get("userconfig", {}).get("hal_type", signal_config.get("hal_type", "float"))
                    direction = signal_config["direction"]
                    boolean = signal_config.get("bool")
                    if netname:
                        if direction in {"input", "output"}:
                            if not boolean:
                                custom.append(f"net rios.{halname} => pyvcp.{halname}")
                                cfgxml_data_status += gui_gen.draw_number(netname, halname, hal_type)
                            else:
                                custom.append(f"net rios.{halname} => pyvcp.{halname}")
                                cfgxml_data_status += gui_gen.draw_led(netname, halname)

        for plugin_instance in self.project.plugin_instances:
            if plugin_instance.plugin_setup.get("joint", False) is False:
                for signal_name, signal_config in plugin_instance.signals().items():
                    halname = signal_config["halname"]
                    varname = signal_config["varname"]
                    netname = signal_config["netname"]
                    direction = signal_config["direction"]
                    boolean = signal_config.get("bool")
                    if halname in self.used_signals:
                        continue
                    if direction == "input" and not netname:
                        custom.append(f"net rios.{halname} <= rio.{halname} => pyvcp.{halname}")
                        if not boolean:
                            vmin = signal_config.get("min", 0)
                            vmax = signal_config.get("max", 1000)
                            cfgxml_data_inputs += gui_gen.draw_number(halname, halname)
                        else:
                            cfgxml_data_inputs += gui_gen.draw_led(halname, halname)

        for plugin_instance in self.project.plugin_instances:
            if plugin_instance.plugin_setup.get("joint", False) is False:
                for signal_name, signal_config in plugin_instance.signals().items():
                    halname = signal_config["halname"]
                    varname = signal_config["varname"]
                    netname = signal_config["netname"]
                    direction = signal_config["direction"]
                    boolean = signal_config.get("bool")
                    if halname in self.used_signals:
                        continue
                    if direction == "output" and not netname:
                        if not boolean:
                            custom.append(f"net rios.{halname} <= pyvcp.{halname}-f => rio.{halname}")
                            vmin = signal_config.get("min", 0)
                            vmax = signal_config.get("max", 1000)
                            cfgxml_data_outputs += gui_gen.draw_scale(halname, halname, vmin, vmax)
                        else:
                            custom.append(f"net rios.{halname} <= pyvcp.{halname} => rio.{halname}")
                            cfgxml_data_outputs += gui_gen.draw_checkbutton(halname, halname)

        cfgxml_data = []
        cfgxml_data += gui_gen.draw_begin()
        cfgxml_data += gui_gen.draw_tabs_begin(["Status", "Outputs", "Inputs"])
        cfgxml_data += gui_gen.draw_tab_begin("Status")
        cfgxml_data += cfgxml_data_status
        cfgxml_data += gui_gen.draw_tab_end()
        cfgxml_data += gui_gen.draw_tab_begin("Outputs")
        cfgxml_data += cfgxml_data_outputs
        cfgxml_data += gui_gen.draw_tab_end()
        cfgxml_data += gui_gen.draw_tab_begin("Inputs")
        cfgxml_data += cfgxml_data_inputs
        cfgxml_data += gui_gen.draw_tab_end()
        cfgxml_data += gui_gen.draw_tabs_end()
        cfgxml_data += gui_gen.draw_end()

        custom.append("")
        open(f"{self.configuration_path}/custom_postgui.hal", "w").write("\n".join(custom))
        open(f"{self.configuration_path}/postgui_call_list.hal", "w").write("\n".join(["source custom_postgui.hal"]))
        open(f"{self.configuration_path}/rio-gui.xml", "w").write("\n".join(cfgxml_data))

    def hal(self):
        output = []

        output.append("# load the realtime components")
        output.append("loadrt [KINS]KINEMATICS")
        output.append("loadrt [EMCMOT]EMCMOT base_period_nsec=[EMCMOT]BASE_PERIOD servo_period_nsec=[EMCMOT]SERVO_PERIOD num_joints=[KINS]JOINTS num_dio=[EMCMOT]NUM_DIO num_aio=[EMCMOT]NUM_AIO")
        output.append("loadrt rio")
        output.append("")

        num_pids = self.num_joints
        output.append(f"loadrt pid num_chan={num_pids}")
        for pidn in range(num_pids):
            output.append(f"addf pid.{pidn}.do-pid-calcs servo-thread")
        output.append("")

        output.append("# add the rio and motion functions to threads")
        output.append("addf motion-command-handler servo-thread")
        output.append("addf motion-controller servo-thread")
        output.append("addf rio.readwrite servo-thread")
        output.append("")
        output.append("# estop loopback")
        output.append("net user-enable-out     <= iocontrol.0.user-enable-out     => rio.enable")
        output.append("net user-request-enable <= iocontrol.0.user-request-enable => rio.enable-request")
        output.append("net rio-status          <= rio.status                      => iocontrol.0.emc-enable-in")
        output.append("")
        output.append("loadusr -W hal_manualtoolchange")
        output.append("net tool-change      hal_manualtoolchange.change   <=  iocontrol.0.tool-change")
        output.append("net tool-changed     hal_manualtoolchange.changed  <=  iocontrol.0.tool-changed")
        output.append("net tool-prep-number hal_manualtoolchange.number   <=  iocontrol.0.tool-prep-number")
        output.append("net tool-prepare-loopback iocontrol.0.tool-prepare => iocontrol.0.tool-prepared")
        output.append("")
        output.append("")

        for plugin_instance in self.project.plugin_instances:
            if plugin_instance.plugin_setup.get("joint", False) is False:
                for signal_name, signal_config in plugin_instance.signals().items():
                    halname = signal_config["halname"]
                    varname = signal_config["varname"]
                    netname = signal_config["netname"]
                    direction = signal_config["direction"]
                    boolean = signal_config.get("bool")
                    if netname:
                        if direction == "input":
                            output.append(f"net rios.{halname} <= rio.{halname}")
                            output.append(f"net rios.{halname} => {netname}")
                        elif direction == "output":
                            output.append(f"net rios.{halname} <= {netname}")
                            output.append(f"net rios.{halname} => rio.{halname}")

        output.append("")

        for axis_name, joints in self.axis_dict.items():
            output.append(f"# Axis: {axis_name}")
            output.append("")
            for joint, joint_setup in joints.items():
                position_mode = joint_setup["position_mode"]
                position_halname = joint_setup["position_halname"]
                feedback_halname = joint_setup["feedback_halname"]
                enable_halname = joint_setup["enable_halname"]
                pin_num = joint_setup["pin_num"]
                if position_mode == "absolute":
                    output.append(f"# joint.{joint}: absolut positioning")
                    output.append(f"net j{joint}pos-cmd        <= joint.{joint}.motor-pos-cmd  => {position_halname}")
                    output.append(f"net j{joint}pos-cmd        => joint.{joint}.motor-pos-fb")
                    if enable_halname:
                        output.append(f"net j{joint}enable         <= joint.{joint}.amp-enable-out => {enable_halname}")
                elif position_halname and feedback_halname:
                    output.append(f"# joint.{joint}: relative positioning using pid.{pin_num}")
                    output.append(f"setp pid.{pin_num}.Pgain     [JOINT_{joint}]P")
                    output.append(f"setp pid.{pin_num}.Igain     [JOINT_{joint}]I")
                    output.append(f"setp pid.{pin_num}.Dgain     [JOINT_{joint}]D")
                    output.append(f"setp pid.{pin_num}.bias      [JOINT_{joint}]BIAS")
                    output.append(f"setp pid.{pin_num}.FF0       [JOINT_{joint}]FF0")
                    output.append(f"setp pid.{pin_num}.FF1       [JOINT_{joint}]FF1")
                    output.append(f"setp pid.{pin_num}.FF2       [JOINT_{joint}]FF2")
                    output.append(f"setp pid.{pin_num}.deadband  [JOINT_{joint}]DEADBAND")
                    output.append(f"setp pid.{pin_num}.maxoutput [JOINT_{joint}]MAXOUTPUT")
                    output.append(f"setp {position_halname}-scale [JOINT_{joint}]SCALE_OUT")
                    output.append(f"setp {feedback_halname}-scale [JOINT_{joint}]SCALE_IN")
                    output.append(f"net j{joint}vel-cmd        <= pid.{pin_num}.output           => {position_halname}")
                    output.append(f"net j{joint}pos-cmd        <= joint.{joint}.motor-pos-cmd  => pid.{pin_num}.command")
                    output.append(f"net j{joint}pos-fb         <= {feedback_halname}     => joint.{joint}.motor-pos-fb")
                    output.append(f"net j{joint}pos-fb         => pid.{joint}.feedback")

                    self.used_signals[feedback_halname.replace("rio.", "")] = f"joint.{joint}.motor-pos-fb"

                    if enable_halname:
                        output.append(f"net j{joint}enable         <= joint.{joint}.amp-enable-out => {enable_halname}")
                    else:
                        output.append(f"net j{joint}enable         <= joint.{joint}.amp-enable-out")
                    output.append(f"net j{joint}enable         => pid.{pin_num}.enable")
                output.append("")

        os.system(f"mkdir -p {self.configuration_path}/")
        open(f"{self.configuration_path}/rio.hal", "w").write("\n".join(output))

    def component_variables(self):
        output = []
        output.append("typedef struct {")
        output.append("    // hal variables")
        output.append(f"    hal_bit_t   *enable;")
        output.append(f"    hal_bit_t   *enable_request;")
        output.append(f"    hal_bit_t   *status;")

        if self.project.multiplexed_output:
            output.append(f"    float MULTIPLEXER_OUTPUT_VALUE;")
            output.append(f"    uint8_t MULTIPLEXER_OUTPUT_ID;")
        if self.project.multiplexed_input:
            output.append(f"    float MULTIPLEXER_INPUT_VALUE;")
            output.append(f"    uint8_t MULTIPLEXER_INPUT_ID;")

        for plugin_instance in self.project.plugin_instances:
            for signal_name, signal_config in plugin_instance.signals().items():
                halname = signal_config["halname"]
                varname = signal_config["varname"]
                direction = signal_config["direction"]
                boolean = signal_config.get("bool")
                hal_type = signal_config.get("userconfig", {}).get("hal_type", signal_config.get("hal_type", "float"))
                if not boolean:
                    output.append(f"    hal_{hal_type}_t *{varname};")
                    if direction == "input" and hal_type == "float":
                        output.append(f"    hal_s32_t *{varname}_S32;")
                    output.append(f"    hal_float_t *{varname}_SCALE;")
                    output.append(f"    hal_float_t *{varname}_OFFSET;")
                else:
                    output.append(f"    hal_bit_t   *{varname};")

        output.append("    // raw variables")
        for (size, plugin_instance, data_name, data_config) in self.project.get_interface_data():
            variable_name = data_config["variable"]
            variable_size = data_config["size"]
            if variable_size > 1:
                output.append(f"    int{variable_size if variable_size != 24 else 32}_t {variable_name};")
            else:
                output.append(f"    bool {variable_name};")
        output.append("")
        output.append("} data_t;")
        output.append("static data_t *data;")
        output.append("")

        output.append("void register_signals(void) {")
        output.append("    int retval = 0;")

        for (size, plugin_instance, data_name, data_config) in self.project.get_interface_data():
            variable_name = data_config["variable"]
            variable_size = data_config["size"]
            if variable_size > 1:
                output.append(f"    data->{variable_name} = 0;")
            else:
                output.append(f"    data->{variable_name} = 0;")
        output.append("")

        output.append(f'    if (retval = hal_pin_bit_newf(HAL_OUT, &(data->status), comp_id, "%s.status", prefix) != 0) error_handler(retval);')
        output.append(f'    if (retval = hal_pin_bit_newf(HAL_IN,  &(data->enable), comp_id, "%s.enable", prefix) != 0) error_handler(retval);')
        output.append(f'    if (retval = hal_pin_bit_newf(HAL_IN,  &(data->enable_request), comp_id, "%s.enable-request", prefix) != 0) error_handler(retval);')
        for plugin_instance in self.project.plugin_instances:
            for signal_name, signal_config in plugin_instance.signals().items():
                halname = signal_config["halname"]
                direction = signal_config["direction"]
                varname = signal_config["varname"]
                boolean = signal_config.get("bool")
                hal_type = signal_config.get("userconfig", {}).get("hal_type", signal_config.get("hal_type", "float"))
                mapping = {"output": "IN", "input": "OUT"}
                hal_direction = mapping[direction]
                if not boolean:
                    output.append(f'    if (retval = hal_pin_float_newf(HAL_IN, &(data->{varname}_SCALE), comp_id, "%s.{halname}-scale", prefix) != 0) error_handler(retval);')
                    output.append(f"    *data->{varname}_SCALE = 1.0;")
                    output.append(f'    if (retval = hal_pin_float_newf(HAL_IN, &(data->{varname}_OFFSET), comp_id, "%s.{halname}-offset", prefix) != 0) error_handler(retval);')
                    output.append(f"    *data->{varname}_OFFSET = 0.0;")
                    output.append(f'    if (retval = hal_pin_{hal_type}_newf(HAL_{hal_direction}, &(data->{varname}), comp_id, "%s.{halname}", prefix) != 0) error_handler(retval);')
                    output.append(f"    *data->{varname} = 0;")
                    if direction == "input" and hal_type == "float":
                        output.append(f'    if (retval = hal_pin_s32_newf(HAL_{hal_direction}, &(data->{varname}_S32), comp_id, "%s.{halname}-s32", prefix) != 0) error_handler(retval);')
                        output.append(f"    *data->{varname}_S32 = 0;")
                else:
                    output.append(f'    if (retval = hal_pin_bit_newf  (HAL_{hal_direction}, &(data->{varname}), comp_id, "%s.{halname}", prefix) != 0) error_handler(retval);')
                    output.append(f"    *data->{varname} = 0;")

        output.append("}")
        output.append("")
        return output

    def component_signal_converter(self):
        output = []
        output.append("// output: SIGOUT -> calc -> VAROUT -> txBuffer")
        for plugin_instance in self.project.plugin_instances:
            for data_name, data_config in plugin_instance.interface_data().items():
                variable_name = data_config["variable"]
                variable_size = data_config["size"]
                if data_config["direction"] == "output":
                    convert_parameter = []
                    for signal_name, signal_config in plugin_instance.signals().items():
                        varname = signal_config["varname"]
                        boolean = signal_config.get("bool")
                        if not boolean:
                            convert_parameter.append(f"volatile hal_float_t *{varname}")
                        else:
                            convert_parameter.append(f"volatile hal_bit_t *{varname}")
                    if variable_size > 1:
                        output.append(f"void convert_{variable_name.lower()}(data_t *data){{")
                    else:
                        output.append(f"void convert_{variable_name.lower()}(data_t *data){{")
                    for parameter in convert_parameter:
                        if data_name.upper() == parameter.split("_")[-1].strip():
                            source = parameter.split()[-1].strip("*")
                            if variable_size > 1:
                                output.append(f"    float value = *data->{source};")
                                output.append(f"    value = value * *data->{source}_SCALE;")
                                output.append(f"    value = value + *data->{source}_OFFSET;")
                            else:
                                output.append(f"    bool value = *data->{source};")
                            data_config["plugin_instance"] = plugin_instance
                            output.append("    " + plugin_instance.convert_c(data_name, data_config).strip())
                            output.append(f"    data->{variable_name} = value;")
                    output.append("}")
                    output.append("")
        output.append("")

        output.append("// input: rxBuffer -> VAROUT -> calc -> SIGOUT")
        for plugin_instance in self.project.plugin_instances:
            for signal_name, signal_config in plugin_instance.signals().items():
                varname = signal_config["varname"]
                if signal_config["direction"] == "input":
                    convert_parameter = []
                    for data_name, data_config in plugin_instance.interface_data().items():
                        variable_name = data_config["variable"]
                        variable_size = data_config["size"]
                        if variable_size > 1:
                            vtype = f"int{variable_size if variable_size != 24 else 32}_t"
                            if variable_size == 8:
                                vtype = f"uint8_t"
                            convert_parameter.append(f"{vtype} *{variable_name}")
                        else:
                            convert_parameter.append(f"bool *{variable_name}")
                    direction = signal_config.get("direction")
                    boolean = signal_config.get("bool")
                    hal_type = signal_config.get("userconfig", {}).get("hal_type", signal_config.get("hal_type", "float"))
                    output.append(f"void convert_{varname.lower()}(data_t *data) {{")
                    for parameter in convert_parameter:
                        if signal_name.upper() == parameter.split("_")[-1].strip():
                            source = parameter.split()[-1].strip("*")
                            if not boolean:
                                output.append(f"    float value = data->{source};")
                                output.append(f"    value = value + *data->{varname}_OFFSET;")
                                output.append(f"    value = value / *data->{varname}_SCALE;")
                            else:
                                output.append(f"    bool value = data->{source};")
                            output.append("    " + plugin_instance.convert_c(signal_name, signal_config).strip())

                            if not boolean and direction == "input" and hal_type == "float":
                                output.append(f"    *data->{varname}_S32 = value;")
                            output.append(f"    *data->{varname} = value;")

                    output.append("}")
                    output.append("")
        output.append("")
        output.append("")
        return output

    def component_buffer_converter(self):
        output = []
        output.append("void convert_outputs(void) {")
        output.append("    // output loop: SIGOUT -> calc -> VAROUT -> txBuffer")
        for plugin_instance in self.project.plugin_instances:
            for data_name, data_config in plugin_instance.interface_data().items():
                variable_name = data_config["variable"]
                if data_config["direction"] == "output":
                    output.append(f"    convert_{variable_name.lower()}(data);")
        output.append("}")
        output.append("")
        output.append("void convert_inputs(void) {")
        output.append("    // input: rxBuffer -> VAROUT -> calc -> SIGOUT")
        for plugin_instance in self.project.plugin_instances:
            for signal_name, signal_config in plugin_instance.signals().items():
                varname = signal_config["varname"]
                if signal_config["direction"] == "input":
                    output.append(f"    convert_{varname.lower()}(data);")
        output.append("}")
        output.append("")
        return output

    def component_buffer(self):
        output = []
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

        output.append("    // copy next multiplexed value")
        output.append(f"    if (data->MULTIPLEXER_OUTPUT_ID < {self.project.multiplexed_output}) {{;")
        output.append("        data->MULTIPLEXER_OUTPUT_ID += 1;")
        output.append("    } else {")
        output.append("        data->MULTIPLEXER_OUTPUT_ID = 0;")
        output.append("    };")
        mpid = 0
        for (size, plugin_instance, data_name, data_config) in self.project.get_interface_data():
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

        for (size, plugin_instance, data_name, data_config) in self.project.get_interface_data():
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

        for (size, plugin_instance, data_name, data_config) in self.project.get_interface_data():
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
        for (size, plugin_instance, data_name, data_config) in self.project.get_interface_data():
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
        header_list = ["rtapi.h", "rtapi_app.h", "hal.h", "unistd.h", "stdlib.h", "stdio.h", "string.h", "math.h", "sys/mman.h"]
        if "serial":
            header_list += ["fcntl.h", "termios.h"]

        module_info = {
            "AUTHOR": "Oliver Dippel",
            "DESCRIPTION": "Driver for RIO FPGA boards",
            "LICENSE": "GPL v2",
        }

        defines = {
            "MODNAME": '"rio"',
            "PREFIX": '"rio"',
            "JOINTS": "3",
            "BUFFER_SIZE": self.project.buffer_bytes,
            "SERIAL_PORT": '"/dev/ttyUSB0"',
            "SERIAL_BAUD": "B1000000",
            "UDP_IP": '"192.168.10.193"',
            "UDP_PORT": 2390,
            "OSC_CLOCK": self.project.config["speed"],
        }

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
        output.append("void rio_readwrite();")
        output.append("int error_handler(int retval);")
        output.append("")

        output += self.component_variables()
        for ppath in glob.glob(f"{os.path.dirname(__file__)}/interfaces/*/*.c"):
            output.append("/*")
            output.append(f"    interface: {os.path.basename(os.path.dirname(ppath))}")
            output.append("*/")
            output.append(open(ppath, "r").read())

        output.append("int interface_init(void) {")
        output.append("    //uart_init();")
        output.append("    udp_init();")
        output.append("}")
        output.append("")

        output.append("")
        output.append("/*")
        output.append(f"    hal functions")
        output.append("*/")

        output.append(open(f"{riocore_path}/files/hal_functions.c", "r").read())
        output += self.component_signal_converter()
        output += self.component_buffer_converter()
        output += self.component_buffer()
        output.append("void rio_readwrite() {")
        output.append("    uint8_t i = 0;")
        output.append("    uint8_t rxBuffer[BUFFER_SIZE * 2];")
        output.append("    uint8_t txBuffer[BUFFER_SIZE * 2];")
        output.append("    if (*data->enable_request == 1) {")
        output.append("        *data->status = 1;")
        output.append("    }")
        output.append("    if (*data->enable == 1 && *data->status == 1) {")
        output.append("        pkg_counter += 1;")
        output.append("        convert_outputs();")
        output.append("        write_txbuffer(txBuffer);")
        output.append("        //uart_trx(txBuffer, rxBuffer, BUFFER_SIZE);")
        output.append("        udp_trx(txBuffer, rxBuffer, BUFFER_SIZE);")
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
        output.append("                *data->status = 0;")
        output.append("            }")
        output.append("        }")
        output.append("    } else {")
        output.append("        *data->status = 0;")
        output.append("    }")
        output.append("}")
        output.append("")
        output.append("")

        os.system(f"mkdir -p {self.component_path}/")
        open(f"{self.component_path}/rio.c", "w").write("\n".join(output))

    def create_axis_config(self):
        pin_num = 0
        self.num_joints = 0
        self.num_axis = 0
        self.axis_dict = {}
        for plugin_instance in self.project.plugin_instances:
            if plugin_instance.plugin_setup.get("joint"):
                axis_num = len(self.axis_dict)
                axis_name = plugin_instance.plugin_setup.get("axis")
                if not axis_name:
                    for name in self.AXIS_NAMES:
                        if name not in self.axis_dict:
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
                position_scale = float(joint_setup["plugin_instance"].plugin_setup.get("scale", 320.0))
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
                feedback = joint_setup["plugin_instance"].plugin_setup.get("feedback")
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
                joint_setup["position_scale"] = position_scale
                joint_setup["feedback_halname"] = feedback_halname
                joint_setup["feedback_scale"] = feedback_scale
                joint_setup["enable_halname"] = enable_halname
                joint_setup["pin_num"] = pin_num
                if position_mode != "absolute":
                    pin_num += 1

        # print("num_joints", self.num_joints)
        # print("num_axis", self.num_axis)
        # print("")


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

    def draw_scale(self, name, halpin, vmin, vmax):
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
        cfgxml_data.append(f"         <number>{display_max}</number>")
        cfgxml_data.append("        </property>")
        cfgxml_data.append('        <property name="max_reading" stdset="0">')
        cfgxml_data.append(f"         <number>{display_max}</number>")
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

    def draw_number(self, name, halpin, hal_type, setup={}):
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

    def draw_checkbutton(self, name, halpin):
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

    def draw_led(self, name, halpin):
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

    def draw_scale(self, name, halpin, vmin, vmax):
        cfgxml_data = []
        cfgxml_data.append("  <hbox>")
        cfgxml_data.append("    <relief>RAISED</relief>")
        cfgxml_data.append("    <bd>2</bd>")
        cfgxml_data.append("    <scale>")
        cfgxml_data.append(f'      <halpin>"{halpin}"</halpin>')
        cfgxml_data.append("      <resolution>0.1</resolution>")
        cfgxml_data.append("      <orient>HORIZONTAL</orient>")
        cfgxml_data.append("      <initval>0</initval>")
        cfgxml_data.append(f"      <min_>{vmin}</min_>")
        cfgxml_data.append(f"      <max_>{vmax}</max_>")
        cfgxml_data.append("      <param_pin>1</param_pin>")
        cfgxml_data.append("    </scale>")
        cfgxml_data.append("    <label>")
        cfgxml_data.append(f'      <text>"{name}"</text>')
        cfgxml_data.append("    </label>")
        cfgxml_data.append("  </hbox>")
        return cfgxml_data

    def draw_meter(self, name, halpin, setup={}, vmin=0, vmax=100):
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
        cfgxml_data.append(f'      <text>"{name}"</text>')
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
        cfgxml_data.append(f'      <text>"{name}"</text>')
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
        display_format = setup.get("size", "05.2f")
        element = "number"
        if hal_type != "float":
            display_format = "d"
            element = hal_type
        cfgxml_data = []
        cfgxml_data.append("  <hbox>")
        cfgxml_data.append("    <relief>RAISED</relief>")
        cfgxml_data.append("    <bd>2</bd>")
        cfgxml_data.append("    <label>")
        cfgxml_data.append(f'      <text>"{name}"</text>')
        cfgxml_data.append("    </label>")
        cfgxml_data.append(f"    <{element}>")
        cfgxml_data.append(f'        <halpin>"{halpin}"</halpin>')
        cfgxml_data.append('        <font>("Helvetica",14)</font>')
        cfgxml_data.append(f'        <format>"{display_format}"</format>')
        cfgxml_data.append(f"    </{element}>")
        cfgxml_data.append("  </hbox>")
        return cfgxml_data

    def draw_checkbutton(self, name, halpin):
        cfgxml_data = []
        cfgxml_data.append("  <hbox>")
        cfgxml_data.append("    <relief>RAISED</relief>")
        cfgxml_data.append("    <bd>2</bd>")
        cfgxml_data.append("    <checkbutton>")
        cfgxml_data.append(f'      <halpin>"{halpin}"</halpin>')
        cfgxml_data.append(f'      <text>"{name}"</text>')
        cfgxml_data.append("    </checkbutton>")
        cfgxml_data.append("  </hbox>")
        return cfgxml_data

    def draw_checkbutton_rgb(self, name, halpin_g, halpin_b, halpin_r):
        cfgxml_data = []
        cfgxml_data.append("  <hbox>")
        cfgxml_data.append("    <relief>RAISED</relief>")
        cfgxml_data.append("    <bd>2</bd>")
        cfgxml_data.append("    <label>")
        cfgxml_data.append(f'      <text>"{name}"</text>')
        cfgxml_data.append("    </label>")
        cfgxml_data.append("    <checkbutton>")
        cfgxml_data.append(f'      <halpin>"{halpin_g}"</halpin>')
        cfgxml_data.append(f'      <text>"G"</text>')
        cfgxml_data.append("    </checkbutton>")
        cfgxml_data.append("    <checkbutton>")
        cfgxml_data.append(f'      <halpin>"{halpin_b}"</halpin>')
        cfgxml_data.append(f'      <text>"B"</text>')
        cfgxml_data.append("    </checkbutton>")
        cfgxml_data.append("    <checkbutton>")
        cfgxml_data.append(f'      <halpin>"{halpin_r}"</halpin>')
        cfgxml_data.append(f'      <text>"R"</text>')
        cfgxml_data.append("    </checkbutton>")
        cfgxml_data.append("  </hbox>")
        return cfgxml_data

    def draw_led(self, name, halpin):
        cfgxml_data = []
        cfgxml_data.append("  <hbox>")
        cfgxml_data.append("    <relief>RAISED</relief>")
        cfgxml_data.append("    <bd>2</bd>")
        cfgxml_data.append("    <led>")
        cfgxml_data.append(f'      <halpin>"{halpin}"</halpin>')
        cfgxml_data.append("      <size>16</size>")
        if halpin.endswith(".R"):
            cfgxml_data.append('      <on_color>"red"</on_color>')
        elif halpin.endswith(".B"):
            cfgxml_data.append('      <on_color>"blue"</on_color>')
        else:
            cfgxml_data.append('      <on_color>"green"</on_color>')
        cfgxml_data.append('      <off_color>"black"</off_color>')
        cfgxml_data.append("    </led>")
        cfgxml_data.append("    <label>")
        cfgxml_data.append(f'      <text>"{name}"</text>')
        cfgxml_data.append("    </label>")
        cfgxml_data.append("  </hbox>")
        return cfgxml_data
