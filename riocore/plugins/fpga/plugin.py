import hashlib
import importlib
import shutil
import stat

import json
import copy
import os
from riocore.plugins import PluginBase
from riocore.generator.cbase import cbase

import riocore

riocore_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))


class Plugin(PluginBase):
    def setup(self):
        self.NAME = "fpga"
        self.COMPONENT = "fpga"
        self.INFO = "fpga board"
        self.DESCRIPTION = "fpga"
        self.KEYWORDS = "fpga board"
        self.TYPE = "base"
        self.IMAGE_SHOW = False
        self.PLUGIN_TYPE = "fpga"
        self.BUILDER = ["clean", "all", "load"]
        self.URL = ""
        self.OPTIONS = {
            "node_type": {
                "default": "Tangbob",
                "type": "select",
                "options": [
                    "Altera10M08Eval",
                    "Basys2",
                    "Colorlight5A-75B-v8.0",
                    "Colorlight5A-75E",
                    "Colorlight_i5-v7_0",
                    "CYC1000",
                    "EBAZ4205",
                    "EP2C5T144",
                    "EP4CE6E22C8",
                    "ICEBreakerV1.0e",
                    "IceShield",
                    "LX9MicroBoard",
                    "Mesa7c80",
                    "Mesa7c81",
                    "MotoMan",
                    "Numato-Spartan6",
                    "OctoBot",
                    "Olimex-ICE40HX8K-EVB",
                    "rioctrl",
                    "Tangbob",
                    "TangNano20K",
                    "TangNano9K",
                    "Tangoboard",
                    "TangPrimer20K",
                    "TangPrimer25K",
                ],
                "description": "board type",
            },
            "simulation": {
                "default": False,
                "type": bool,
                "description": "simulation mode",
            },
        }

        node_type = self.plugin_setup.get("node_type", self.option_default("node_type"))
        if not self.plugin_setup.get("node_type"):
            return

        board_file = os.path.join(os.path.dirname(__file__), f"{node_type}.json")
        self.jdata = json.loads(open(board_file, "r").read())

        if self.jdata.get("toolchains"):
            self.OPTIONS.update(
                {
                    "toolchain": {
                        "default": self.jdata.get("toolchain"),
                        "type": "select",
                        "options": self.jdata["toolchains"],
                    }
                }
            )

        self.OPTIONS.update(
            {
                "speed": {
                    "default": int(self.jdata["clock"].get("speed")),
                    "type": int,
                    "min": 1000000,
                    "max": 500000000,
                }
            }
        )

        self.IMAGE = f"{node_type}.png"
        self.IMAGE_SHOW = True
        self.DESCRIPTION = self.jdata.get("comment", "")
        self.INFO = self.jdata.get("description", "")
        self.PINDEFAULTS = {}
        for slot in self.jdata["slots"]:
            slot_name = slot["name"]
            for pin_name, pin_data in slot["pins"].items():
                if isinstance(pin_data, str):
                    pin_data = {"pin": pin_data}
                self.PINDEFAULTS[f"{slot_name}:{pin_name}"] = {
                    "edge": "source",
                    "optional": True,
                    "pintype": "FPGA",
                    "type": ["FPGA"],
                    "pin": pin_data["pin"],
                    "pos": pin_data.get("pos", (0, 0)),
                    "direction": pin_data.get("direction", "all"),
                }

        self.fpga_num = 0
        self.hal_prefix = "rio"

        toolchain = self.plugin_setup.get("toolchain", self.option_default("toolchain"))
        speed = self.plugin_setup.get("speed", self.option_default("speed"))
        self.jdata["toolchain"] = toolchain
        self.jdata["speed"] = speed
        self.jdata["osc_clock"] = int(self.jdata["clock"].get("osc_clock", self.jdata["speed"]))
        self.jdata["sysclk_pin"] = self.jdata["clock"]["pin"]

    def update_system_setup(self, parent):
        self.system_setup["speed"] = self.jdata["speed"]

    def hal(self, parent):
        parent.halg.fmt_add_top(f"addf {self.hal_prefix}.readwrite servo-thread")
        parent.halg.net_add("iocontrol.0.user-enable-out", f"{self.hal_prefix}.sys-enable", "user-enable-out")
        parent.halg.net_add("iocontrol.0.user-request-enable", f"{self.hal_prefix}.sys-enable-request", "user-request-enable")
        parent.halg.net_add(f"&{self.hal_prefix}.sys-status", "iocontrol.0.emc-enable-in")
        parent.halg.net_add("halui.machine.is-on", f"{self.hal_prefix}.machine-on")

    def component_loader(cls, instances):
        output = []
        for instance in instances:
            node_type = instance.plugin_setup.get("node_type", instance.option_default("node_type"))
            simulation = instance.plugin_setup.get("simulation", instance.option_default("simulation"))
            output.append(f"# fpga board {node_type}")
            output.append("loadrt rio")
            output.append("")
            output.append("# if you need to test rio without hardware, set it to 1")
            if simulation:
                output.append(f"setp {instance.hal_prefix}.sys-simulation 1")
            else:
                output.append(f"setp {instance.hal_prefix}.sys-simulation 0")
            output.append("")
            output.append("addf rio.readwrite servo-thread")
        return "\n".join(output)

    def builder(self, config, command):
        project = riocore.Project(copy.deepcopy(config))
        gateware_path = os.path.join(project.config["output_path"], "Gateware", self.instances_name)
        cmd = f"cd {gateware_path} && make {command}"
        return cmd

    def extra_files(cls, parent, instances):
        for instance in instances:
            gateware_path = os.path.join(parent.project.config["output_path"], "Gateware", instance.instances_name)
            instance.jdata["name"] = instance.plugin_setup.get("node_type", instance.option_default("node_type"))
            instance.jdata["json_path"] = parent.project.config["json_path"]
            instance.jdata["riocore_path"] = riocore_path
            instance.jdata["output_path"] = gateware_path

            # clean None pins
            for plugin_instance in parent.project.plugin_instances:
                if plugin_instance.PLUGIN_TYPE != "gateware":
                    continue
                for pin_name, pin_config in plugin_instance.plugin_setup.get("pins", {}).items():
                    if "pin" in pin_config and not pin_config["pin"]:
                        del pin_config["pin"]
            cls.generator(parent)

            component(parent.project)

    def generator(cls, parent, generate_pll=True):
        os.makedirs(cls.jdata["output_path"], exist_ok=True)

        toolchains_json_path = os.path.join(riocore_path, "toolchains.json")
        if os.path.isfile(toolchains_json_path):
            cls.jdata["toolchains_json"] = json.loads(open(toolchains_json_path, "r").read())
            if cls.jdata["toolchains_json"]:
                for toolchain, path in cls.jdata["toolchains_json"].items():
                    if path and not os.path.isdir(path):
                        riocore.log(f"WARNING: toolchains.json: path for '{toolchain}' not found: {path}")
        else:
            open(toolchains_json_path, "w").write(
                json.dumps(
                    {
                        "gowin": "",
                        "diamond": "",
                        "vivado": "",
                        "quartus": "",
                        "icestorm": "",
                        "ise": "",
                        "efinity": "",
                    },
                    indent=4,
                )
            )

        parent.generate_pll = generate_pll
        riocore.log(f"loading toolchain {cls.jdata['toolchain']}")
        cls.jdata["toolchain_generator"] = importlib.import_module(".toolchain", f"riocore.generator.toolchains.{cls.jdata['toolchain']}").Toolchain(cls.jdata)

        for plugin_instance in parent.project.plugin_instances:
            if plugin_instance.PLUGIN_TYPE != "gateware":
                continue
            plugin_instance.post_setup(parent.project)

        parent.expansion_pins = []
        for plugin_instance in parent.project.plugin_instances:
            if plugin_instance.PLUGIN_TYPE != "gateware":
                continue
            for pin in plugin_instance.expansion_outputs():
                parent.expansion_pins.append(pin)
            for pin in plugin_instance.expansion_inputs():
                parent.expansion_pins.append(pin)

        parent.virtual_pins = []
        for plugin_instance in parent.project.plugin_instances:
            if plugin_instance.PLUGIN_TYPE != "gateware":
                continue
            for pin_name, pin_config in plugin_instance.pins().items():
                if "pin" in pin_config and pin_config.get("pin") and pin_config["pin"].startswith("VIRT:"):
                    pinname = pin_config["pin"]
                    if pinname not in parent.virtual_pins:
                        parent.virtual_pins.append(pinname)

        parent.verilogs = []
        parent.linked_pins = []
        cls.globals(parent)
        cls.top(parent)
        cls.makefile(parent)

    def globals(cls, parent):
        # create globals.v for compatibility functions
        globals_data = []
        globals_data.append(f'localparam FPGA_FAMILY = "{cls.jdata.get("family", "UNKNOWN")}";')
        globals_data.append(f'localparam FPGA_TYPE = "{cls.jdata.get("type", "UNKNOWN")}";')
        globals_data.append(f'localparam TOOLCHAIN = "{cls.jdata["toolchain"]}";')
        globals_data.append("")
        if cls.jdata.get("family", "UNKNOWN") in {"ice40"}:
            globals_data.append("`define DSP_CALC")
        globals_data.append("")
        globals_data.append("// replacement for $clog2")
        globals_data.append("function integer clog2;")
        globals_data.append("  input integer value;")
        globals_data.append("  begin")
        globals_data.append("    value = value-1;")
        globals_data.append("    for (clog2=0; value>0; clog2=clog2+1)")
        globals_data.append("      value = value>>1;")
        globals_data.append("  end")
        globals_data.append("endfunction")
        globals_data.append("")
        open(os.path.join(cls.jdata["output_path"], "globals.v"), "w").write("\n".join(globals_data))
        parent.verilogs.append("globals.v")

    def makefile(cls, parent):
        flashcmd = cls.jdata.get("flashcmd")
        if flashcmd:
            if flashcmd.startswith("./") and parent.jdata["json_path"]:
                flashcmd_script = flashcmd.split()[0].replace("./", "")
                json_path = parent.jdata["json_path"]
                flashcmd_script_path = os.path.join(json_path, flashcmd_script)
                riocore.log(flashcmd_script_path)
                if os.path.isfile(flashcmd_script_path):
                    target = os.path.join(cls.jdata["output_path"], flashcmd_script)
                    shutil.copy(flashcmd_script_path, target)
                    os.chmod(target, stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR | stat.S_IRGRP | stat.S_IXGRP | stat.S_IROTH | stat.S_IXOTH)

        for plugin_instance in parent.project.plugin_instances:
            if plugin_instance.PLUGIN_TYPE != "gateware":
                continue
            for verilog in plugin_instance.gateware_files():
                if verilog in parent.verilogs:
                    continue
                parent.verilogs.append(verilog)
                ipv_path = os.path.join(riocore_path, "plugins", plugin_instance.NAME, verilog)
                if not os.path.isfile(ipv_path):
                    # fallback to shared files
                    ipv_path = os.path.join(riocore_path, "files", "verilog", verilog)
                if not os.path.isfile(ipv_path):
                    riocore.log(f"ERROR: can not found verilog file: {verilog}")
                    exit(1)
                target = os.path.join(cls.jdata["output_path"], verilog)
                shutil.copy(ipv_path, target)

            for verilog, data in plugin_instance.gateware_virtual_files().items():
                if verilog in parent.verilogs:
                    continue
                if not verilog.endswith(".mem"):
                    parent.verilogs.append(verilog)
                target = os.path.join(cls.jdata["output_path"], verilog)
                open(target, "w").write(data)

        for extrafile in ("debouncer.v", "toggle.v", "pwmmod.v", "oneshot.v", "delay.v"):
            parent.verilogs.append(extrafile)
            source = os.path.join(riocore_path, "files", "verilog", extrafile)
            target = os.path.join(cls.jdata["output_path"], extrafile)
            shutil.copy(source, target)
        parent.verilogs.append("rio.v")
        cls.jdata["verilog_files"] = parent.verilogs
        cls.jdata["pinlists"] = {}
        cls.jdata["pinlists"]["base"] = {}
        cls.jdata["pinlists"]["base"]["sysclk_in"] = {"direction": "input", "pull": None, "pin": cls.jdata["sysclk_pin"], "varname": "sysclk_in"}

        cls.jdata["timing_constraints"] = {}
        cls.jdata["timing_constraints_instance"] = {}
        for plugin_instance in parent.project.plugin_instances:
            if plugin_instance.PLUGIN_TYPE != "gateware":
                continue
            for key, value in plugin_instance.timing_constraints().items():
                if ":" in key:
                    pre, post = key.split(":")
                    pname = f"{pre}_{plugin_instance.instances_name}_{post}".upper()
                    cls.jdata["timing_constraints"][pname] = value
                else:
                    cls.jdata["timing_constraints_instance"][f"{plugin_instance.instances_name}.{key}"] = value

        parent.pinmapping = {}
        parent.pinmapping_rev = {}
        parent.slots = cls.jdata.get("board_data", {}).get("slots", []) + cls.jdata.get("slots", [])
        for slot in parent.slots:
            slot_name = slot.get("name")
            slot_pins = slot.get("pins", {})
            for pin_name, pin in slot_pins.items():
                if isinstance(pin, dict):
                    pin = pin["pin"]
                pin_id = f"{slot_name}:{pin_name}"
                parent.pinmapping[pin_id] = pin
                parent.pinmapping_rev[pin] = pin_id

        pinnames = {}
        for plugin_instance in parent.project.plugin_instances:
            if plugin_instance.PLUGIN_TYPE != "gateware":
                continue
            cls.jdata["pinlists"][plugin_instance.instances_name] = {}
            for pin_name, pin_config in plugin_instance.pins().items():
                if "pin" in pin_config and pin_config["pin"] not in parent.expansion_pins and pin_config["pin"] not in parent.virtual_pins and pin_config["varname"] not in parent.linked_pins:
                    pin_config["pin"] = parent.pinmapping.get(pin_config["pin"], pin_config["pin"])
                    cls.jdata["pinlists"][plugin_instance.instances_name][pin_name] = pin_config
                    if pin_config["pin"] not in pinnames:
                        pinnames[pin_config["pin"]] = plugin_instance.instances_name
                    else:
                        riocore.log(f"ERROR: pin allready exist {pin_config['pin']} ({plugin_instance.instances_name} / {pinnames[pin_config['pin']]})")

        cls.jdata["toolchain_generator"].generate(cls.jdata["output_path"])

    def top(cls, parent):
        output = []
        input_variables_list = ["header_tx[7:0], header_tx[15:8], header_tx[23:16], header_tx[31:24]"]
        input_variables_list += ["timestamp[7:0], timestamp[15:8], timestamp[23:16], timestamp[31:24]"]
        output_variables_list = []
        parent.iface_in = []
        parent.iface_out = []
        output_pos = parent.project.buffer_size

        variable_name = "header_rx"
        size = 32
        pack_list = []
        for bit_num in range(0, size, 8):
            pack_list.append(f"rx_data[{output_pos - 1}:{output_pos - 8}]")
            output_pos -= 8
        output_variables_list.append(f"// PC -> FPGA ({parent.project.output_size} + FILL)")
        output_variables_list.append(f"// assign {variable_name} = {{{', '.join(reversed(pack_list))}}};")
        parent.iface_out.append(["RX_HEADER", size])
        parent.iface_in.append(["TX_HEADER", size])
        parent.iface_in.append(["TITMESTAMP", size])

        if parent.project.multiplexed_input:
            variable_name = "MULTIPLEXED_INPUT_VALUE"
            size = parent.project.multiplexed_input_size
            pack_list = []
            for bit_num in range(0, size, 8):
                pack_list.append(f"{variable_name}[{bit_num + 7}:{bit_num}]")
            input_variables_list.append(f"{', '.join(pack_list)}")
            parent.iface_in.append([variable_name, size])
            variable_name = "MULTIPLEXED_INPUT_ID"
            size = 8
            pack_list = []
            for bit_num in range(0, size, 8):
                pack_list.append(f"{variable_name}[{bit_num + 7}:{bit_num}]")
            input_variables_list.append(f"{', '.join(pack_list)}")
            parent.iface_in.append([variable_name, size])

        if parent.project.multiplexed_output:
            variable_name = "MULTIPLEXED_OUTPUT_VALUE"
            size = parent.project.multiplexed_output_size
            pack_list = []
            for bit_num in range(0, size, 8):
                pack_list.append(f"rx_data[{output_pos - 1}:{output_pos - 8}]")
                output_pos -= 8
            output_variables_list.append(f"assign {variable_name} = {{{', '.join(reversed(pack_list))}}};")
            parent.iface_out.append([variable_name, size])
            variable_name = "MULTIPLEXED_OUTPUT_ID"
            size = 8
            pack_list = []
            for bit_num in range(0, size, 8):
                pack_list.append(f"rx_data[{output_pos - 1}:{output_pos - 8}]")
                output_pos -= 8
            output_variables_list.append(f"assign {variable_name} = {{{', '.join(reversed(pack_list))}}};")
            parent.iface_out.append([variable_name, size])

        for size, plugin_instance, data_name, data_config in parent.project.get_interface_data():
            multiplexed = data_config.get("multiplexed", False)
            if multiplexed:
                continue
            variable_name = data_config["variable"]
            if data_config["direction"] == "input":
                if not data_config.get("expansion"):
                    pack_list = []
                    if size >= 8:
                        for bit_num in range(0, size, 8):
                            pack_list.append(f"{variable_name}[{bit_num + 7}:{bit_num}]")
                    else:
                        pack_list.append(f"{variable_name}")
                    input_variables_list.append(f"{', '.join(pack_list)}")
                    parent.iface_in.append([variable_name, size])
            elif data_config["direction"] == "output":
                if not data_config.get("expansion"):
                    pack_list = []
                    if size >= 8:
                        for bit_num in range(0, size, 8):
                            pack_list.append(f"rx_data[{output_pos - 1}:{output_pos - 8}]")
                            output_pos -= 8
                    elif size > 1:
                        pack_list.append(f"rx_data[{output_pos - 1}:{output_pos - size}]")
                        output_pos -= size
                    else:
                        pack_list.append(f"rx_data[{output_pos - 1}]")
                        output_pos -= 1
                    output_variables_list.append(f"assign {variable_name} = {{{', '.join(reversed(pack_list))}}};")
                    parent.iface_out.append([variable_name, size])

        if parent.project.buffer_size > parent.project.input_size:
            diff = parent.project.buffer_size - parent.project.input_size
            input_variables_list.append(f"{diff}'d0")

        diff = parent.project.buffer_size - parent.project.output_size
        if parent.project.buffer_size > parent.project.output_size:
            output_variables_list.append(f"// assign FILL = rx_data[{diff - 1}:0];")

        if output_pos != diff:
            riocore.log("ERROR: wrong buffer sizes")
            exit(1)

        arguments_list = ["input sysclk_in"]
        existing_pins = {}
        double_pins = {}
        for plugin_instance in parent.project.plugin_instances:
            if plugin_instance.PLUGIN_TYPE != "gateware":
                continue
            for pin_name, pin_config in plugin_instance.pins().items():
                if "pin" in pin_config and pin_config["pin"] not in parent.expansion_pins and pin_config["pin"] not in parent.virtual_pins:
                    if pin_config["pin"] in existing_pins:
                        double_pins[pin_config["pin"]] = pin_config["varname"]

                    else:
                        arguments_list.append(f"{pin_config['direction'].lower()} {pin_config['varname']}")
                        existing_pins[pin_config["pin"]] = pin_config["varname"]

        output.append("/*")
        output.append(f"    ######### {cls.jdata['name']} #########")
        output.append("")
        output.append("")
        for key in ("toolchain", "family", "type", "package"):
            value = cls.jdata[key]
            output.append(f"    {key.title():10}: {value}")
        output.append(f"    Clock     : {(cls.jdata['speed'] / 1000000)} Mhz")
        output.append("")
        for plugin_instance in parent.project.plugin_instances:
            if plugin_instance.PLUGIN_TYPE != "gateware":
                continue
            for pin_name, pin_config in plugin_instance.pins().items():
                if "pin" in pin_config and pin_config["pin"] not in parent.expansion_pins:
                    pull = f"PULL{pin_config.get('pull').upper()}" if pin_config.get("pull") else ""
                    if pin_config["direction"] == "input":
                        output.append(f"    {pin_config['varname']} <- {pin_config['pin']} {pull}")
                    elif pin_config["direction"] == "output":
                        output.append(f"    {pin_config['varname']} -> {pin_config['pin']} {pull}")
                    else:
                        output.append(f"    {pin_config['varname']} <> {pin_config['pin']} {pull}")
        output.append("")
        output.append("*/")
        output.append("")
        output.append("/* verilator lint_off UNUSEDSIGNAL */")
        output.append("")
        output.append("module rio (")

        for plugin_instance in parent.project.plugin_instances:
            if plugin_instance.PLUGIN_TYPE != "gateware":
                continue
            if plugin_instance.PASSTHROUGH:
                output.append(f"        // {plugin_instance.instances_name}")
                for name, data in plugin_instance.PASSTHROUGH.items():
                    direction = data["direction"]
                    size = data.get("size", 1)
                    if size > 1:
                        output.append(f"        {direction} wire [{size - 1}:0] {name},")
                    else:
                        output.append(f"        {direction} wire {name},")

        output.append("        // RIO")
        arguments_string = ",\n        ".join(arguments_list)
        output.append(f"        {arguments_string}")
        output.append("    );")
        output.append("")
        output.append(f"    localparam BUFFER_SIZE = 16'd{parent.project.buffer_size}; // {parent.project.buffer_size // 8} bytes")
        output.append("")
        output.append("    reg INTERFACE_TIMEOUT = 0;")
        output.append("    wire INTERFACE_SYNC;")

        error_signals = ["INTERFACE_TIMEOUT"]
        for plugin_instance in parent.project.plugin_instances:
            if plugin_instance.PLUGIN_TYPE != "gateware":
                continue
            for data_name, interface_setup in plugin_instance.interface_data().items():
                error_on = interface_setup.get("error_on")
                if error_on is True:
                    error_signals.append(interface_setup["variable"])
                elif error_on is False:
                    error_signals.append(f"~{interface_setup['variable']}")

        output.append("    wire ERROR;")
        output.append(f"    assign ERROR = ({' | '.join(error_signals)});")
        output.append("")

        osc_clock = cls.jdata["osc_clock"]
        speed = cls.jdata["speed"]
        if osc_clock and float(osc_clock) != float(speed):
            if parent.generate_pll:
                if hasattr(cls.jdata["toolchain_generator"], "pll"):
                    cls.jdata["toolchain_generator"].pll(float(osc_clock), float(speed))
                else:
                    riocore.log(f"WARNING: can not generate pll for this platform: set speed to: {speed} Hz")
                    cls.jdata["speed"] = speed
            else:
                riocore.log("INFO: preview-mode / no pll generated")

            if cls.jdata["family"] == "Trion":
                output.append("    wire sysclk;")
                output.append("    assign sysclk = sysclk_in;")
            else:
                parent.verilogs.append("pll.v")
                output.append("    wire sysclk;")
                output.append("    wire locked;")
                if cls.jdata["family"] == "MAX 10":
                    output.append("    pll mypll(.inclk0(sysclk_in), .c0(sysclk), .locked(locked));")
                elif cls.jdata["family"] == "xc7":
                    output.append("    wire sysclk25;")
                    output.append("    wire reset;")
                    output.append("    pll mypll(.clock_in(sysclk_in), .clock_out(sysclk), .clock25_out(sysclk25), .locked(locked), .reset(reset));")
                else:
                    output.append("    pll mypll(sysclk_in, sysclk, locked);")
        else:
            output.append("    wire sysclk;")
            output.append("    assign sysclk = sysclk_in;")
        output.append("")

        sysclk_speed = cls.jdata["speed"]
        output.append("    reg[2:0] INTERFACE_SYNCr;  always @(posedge sysclk) INTERFACE_SYNCr <= {INTERFACE_SYNCr[1:0], INTERFACE_SYNC};")
        output.append("    wire INTERFACE_SYNC_RISINGEDGE = (INTERFACE_SYNCr[2:1]==2'b01);")
        output.append("")

        output.append(f"    parameter TIMEOUT = {sysclk_speed // 10};")
        output.append("    localparam TIMEOUT_BITS = clog2(TIMEOUT + 1);")
        output.append("    reg [TIMEOUT_BITS:0] timeout_counter = 0;")
        output.append("")
        output.append("    always @(posedge sysclk) begin")
        output.append("        if (INTERFACE_SYNC_RISINGEDGE == 1) begin")
        output.append("            timeout_counter <= 0;")
        output.append("        end else begin")
        output.append("            if (timeout_counter < TIMEOUT) begin")
        output.append("                timeout_counter <= timeout_counter + 1'd1;")
        output.append("                INTERFACE_TIMEOUT <= 0;")
        output.append("            end else begin")
        output.append("                INTERFACE_TIMEOUT <= 1;")
        output.append("            end")
        output.append("        end")
        output.append("    end")
        output.append("")
        output.append("    wire [BUFFER_SIZE-1:0] rx_data;")
        output.append("    wire [BUFFER_SIZE-1:0] tx_data;")
        output.append("")
        output.append("    reg [31:0] timestamp = 0;")
        output.append("    reg signed [31:0] header_tx = 32'h64617461;")
        output.append("    always @(posedge sysclk) begin")
        output.append("        timestamp <= timestamp + 1'd1;")
        output.append("    end")
        output.append("")

        if double_pins:
            output.append("// linking double used input pins")
            for pin, varname in double_pins.items():
                if varname.startswith("PININ_"):
                    output.append(f"    wire {varname};")
                    output.append(f"    assign {varname} = {existing_pins[pin]};")
                    if not existing_pins[pin].startswith("PININ_"):
                        riocore.log(f"ERROR: can not share input pin with output pin: {existing_pins[pin]} -> {pin} -> {varname}")
                    else:
                        riocore.log(f"WARNING: input pin ({pin}) assigned to multiple plugins: {varname} / {existing_pins[pin]}")
                    parent.linked_pins.append(varname)
                else:
                    riocore.log(f"ERROR: can not assign output pin to multiple plugins: {varname} / {existing_pins[pin]} -> {pin}")

        # virtual pins
        for pin in parent.virtual_pins:
            pinname = pin.replace(":", "_")
            output.append(f"    wire {pinname};")

        for plugin_instance in parent.project.plugin_instances:
            if plugin_instance.PLUGIN_TYPE != "gateware":
                continue
            for pin_name, pin_config in plugin_instance.pins().items():
                if "pin" in pin_config and pin_config["pin"] in parent.virtual_pins:
                    pinname = pin_config["pin"].replace(":", "_")
                    if pin_config["direction"] == "output":
                        output.append(f"    wire {pin_config['varname']};")
                        output.append(f"    assign {pinname} = {pin_config['varname']}; // {pin_config['direction']}")
                    elif pin_config["direction"] == "input":
                        output.append(f"    wire {pin_config['varname']};")
                        output.append(f"    assign {pin_config['varname']} = {pinname}; // {pin_config['direction']}")

        # multiplexing
        if parent.project.multiplexed_input:
            output.append(f"    reg [{parent.project.multiplexed_input_size - 1}:0] MULTIPLEXED_INPUT_VALUE = 0;")
            output.append("    reg [7:0] MULTIPLEXED_INPUT_ID = 0;")
        if parent.project.multiplexed_output:
            output.append(f"    wire [{parent.project.multiplexed_output_size - 1}:0] MULTIPLEXED_OUTPUT_VALUE;")
            output.append("    wire [7:0] MULTIPLEXED_OUTPUT_ID;")

        for plugin_instance in parent.project.plugin_instances:
            if plugin_instance.PLUGIN_TYPE != "gateware":
                continue
            for data_name, data_config in plugin_instance.interface_data().items():
                if not data_config.get("expansion"):
                    variable_name = data_config["variable"]
                    variable_size = data_config["size"]
                    direction = data_config["direction"]
                    multiplexed = data_config.get("multiplexed", False)
                    if variable_size > 1:
                        if multiplexed and direction == "output":
                            output.append(f"    reg [{variable_size - 1}:0] {variable_name} = 0;")
                        else:
                            output.append(f"    wire [{variable_size - 1}:0] {variable_name};")
                    else:
                        if multiplexed and direction == "output":
                            output.append(f"    reg {variable_name};")
                        else:
                            output.append(f"    wire {variable_name};")
        output.append("")

        output_variables_string = "\n    ".join(output_variables_list)
        output.append(f"    {output_variables_string}")
        output.append("")
        output.append(f"    // FPGA -> PC ({parent.project.input_size} + FILL)")
        output.append("    assign tx_data = {")
        input_variables_string = ",\n        ".join(input_variables_list)
        output.append(f"        {input_variables_string}")
        output.append("    };")
        output.append("")

        # gateware_defines
        for plugin_instance in parent.project.plugin_instances:
            if plugin_instance.PLUGIN_TYPE != "gateware":
                continue
            define_string = "\n    ".join(plugin_instance.gateware_defines())
            if define_string:
                output.append(f"    {define_string}")
        output.append("")

        # expansion assignments
        used_expansion_outputs = []
        for plugin_instance in parent.project.plugin_instances:
            if plugin_instance.PLUGIN_TYPE != "gateware":
                continue
            for pin_name, pin_config in plugin_instance.pins().items():
                if "pin" in pin_config:
                    if pin_config["pin"] in parent.expansion_pins:
                        output.append(f"    wire {pin_config['varname']};")

        for plugin_instance in parent.project.plugin_instances:
            if plugin_instance.PLUGIN_TYPE != "gateware":
                continue
            for pin_name, pin_config in plugin_instance.pins().items():
                if "pin" in pin_config:
                    if pin_config["pin"] in parent.expansion_pins:
                        if pin_config["direction"] == "input":
                            output.append(f"    assign {pin_config['varname']} = {pin_config['pin']};")
                        elif pin_config["direction"] == "output":
                            used_expansion_outputs.append(pin_config["pin"])

        if parent.expansion_pins:
            output_exp = []
            # update expansion output pins
            for plugin_instance in parent.project.plugin_instances:
                if plugin_instance.PLUGIN_TYPE != "gateware":
                    continue
                for pin_name, pin_config in plugin_instance.pins().items():
                    if "pin" in pin_config:
                        if pin_config["pin"] in parent.expansion_pins:
                            if pin_config["direction"] == "output":
                                output_exp.append(f"        {pin_config['pin']} <= {pin_config['varname']};")
            # set expansion output pins without driver
            for plugin_instance in parent.project.plugin_instances:
                if plugin_instance.PLUGIN_TYPE != "gateware":
                    continue
                for data_name, data_config in plugin_instance.interface_data().items():
                    if data_config.get("expansion"):
                        direction = data_config["direction"]
                        variable = data_config["variable"]
                        size = data_config["size"]
                        bit_n = data_config["bit"]
                        if direction == "output":
                            default = data_config.get("default", 0)
                            if size == 1:
                                if variable not in used_expansion_outputs:
                                    output_exp.append(f"        {variable} <= {size}'d{default};")
                            else:
                                for bit_num in range(0, size):
                                    bitvar = f"{variable}[{bit_num}]"
                                    if bitvar not in used_expansion_outputs:
                                        if default & (1 << bit_n):
                                            output_exp.append(f"        {bitvar} <= 1'd1;")
                                        else:
                                            output_exp.append(f"        {bitvar} <= 1'd0;")
            if output_exp:
                output.append("    // update expansion output pins")
                output.append("    always @(posedge sysclk) begin")
                output += output_exp
                output.append("    end")

        if parent.project.multiplexed_input:
            output.append("    always @(posedge sysclk) begin")
            output.append("        if (INTERFACE_SYNC_RISINGEDGE == 1) begin")
            output.append(f"            if (MULTIPLEXED_INPUT_ID < {parent.project.multiplexed_input - 1}) begin")
            output.append("                MULTIPLEXED_INPUT_ID = MULTIPLEXED_INPUT_ID + 1'd1;")
            output.append("            end else begin")
            output.append("                MULTIPLEXED_INPUT_ID = 0;")
            output.append("            end")
            mpid = 0
            for size, plugin_instance, data_name, data_config in parent.project.get_interface_data():
                multiplexed = data_config.get("multiplexed", False)
                if not multiplexed:
                    continue
                variable_name = data_config["variable"]
                direction = data_config["direction"]
                if direction == "input":
                    output.append(f"            if (MULTIPLEXED_INPUT_ID == {mpid}) begin")
                    if size == 1:
                        output.append(f"                MULTIPLEXED_INPUT_VALUE <= {variable_name};")
                    else:
                        output.append(f"                MULTIPLEXED_INPUT_VALUE <= {variable_name}[{size - 1}:0];")
                    output.append("            end")
                    mpid += 1
            output.append("        end")
            output.append("    end")

        if parent.project.multiplexed_output:
            output.append("    always @(posedge sysclk) begin")
            mpid = 0
            for size, plugin_instance, data_name, data_config in parent.project.get_interface_data():
                multiplexed = data_config.get("multiplexed", False)
                if not multiplexed:
                    continue
                variable_name = data_config["variable"]
                direction = data_config["direction"]
                if direction == "output":
                    output.append(f"        if (MULTIPLEXED_OUTPUT_ID == {mpid}) begin")
                    output.append(f"            {variable_name} <= MULTIPLEXED_OUTPUT_VALUE[{size - 1}:0];")
                    output.append("        end")
                    mpid += 1
            output.append("    end")

        varmapping = {}
        for plugin_instance in parent.project.plugin_instances:
            if plugin_instance.PLUGIN_TYPE != "gateware":
                continue
            for signal, signal_config in plugin_instance.SIGNALS.items():
                if signal in plugin_instance.INTERFACE:
                    iface = plugin_instance.INTERFACE[signal]
                    varmapping[f"{signal_config['signal_prefix']}:{signal}"] = iface["variable"]

        # gateware instances
        for plugin_instance in parent.project.plugin_instances:
            if plugin_instance.PLUGIN_TYPE != "gateware":
                continue
            if not plugin_instance.gateware_instances():
                continue
            output.append("")
            output.append(f"    // Name: {plugin_instance.plugin_setup.get('name', plugin_instance.instances_name)} ({plugin_instance.NAME})")

            output_first = []
            output_last = []
            for instance_name, instance_config in plugin_instance.gateware_instances().items():
                instance_module = instance_config.get("module")
                instance_parameter = instance_config.get("parameter")
                instance_arguments = instance_config.get("arguments")
                instance_predefines = instance_config.get("predefines")
                instance_direct = instance_config.get("direct")
                if instance_predefines:
                    for part in instance_predefines:
                        if "wire " in part:
                            output_first.append(f"    {part}")
                        else:
                            output_last.append(f"    {part}")
                if not instance_direct:
                    if instance_arguments:
                        if instance_parameter:
                            output_last.append(f"    {instance_module} #(")
                            parameters_list = []
                            for parameter_name, parameter_value in instance_parameter.items():
                                parameters_list.append(f".{parameter_name}({parameter_value})")
                            parameters_string = ",\n        ".join(parameters_list)
                            output_last.append(f"        {parameters_string}")
                            output_last.append(f"    ) {instance_name} (")
                        else:
                            output_last.append(f"    {instance_module} {instance_name} (")
                        arguments_list = []
                        for argument_name, argument_value in instance_arguments.items():
                            if ":" in argument_value:
                                if argument_value in varmapping:
                                    argument_value = varmapping[argument_value]
                                else:
                                    riocore.log(f"ERROR: no mapping found: {argument_value}")
                            arguments_list.append(f".{argument_name}({argument_value})")

                        arguments_string = ",\n        ".join(arguments_list)
                        output_last.append(f"        {arguments_string}")
                        output_last.append("    );")
            output += output_first
            output += output_last

        output.append("")
        output.append("endmodule")
        output.append("")
        riocore.log(f"writing gateware to: {cls.jdata['output_path']}")
        open(os.path.join(cls.jdata["output_path"], "rio.v"), "w").write("\n".join(output))

        # write hash of rio.v to filesystem
        hash_file_compiled = os.path.join(cls.jdata["output_path"], "hash_compiled.txt")
        hash_compiled = ""
        if os.path.isfile(hash_file_compiled):
            hash_compiled = open(hash_file_compiled, "r").read()

        hash_file_flashed = os.path.join(cls.jdata["output_path"], "hash_flashed.txt")
        hash_flashed = ""
        if os.path.isfile(hash_file_flashed):
            hash_flashed = open(hash_file_flashed, "r").read()

        hash_md5 = hashlib.md5()
        with open(os.path.join(cls.jdata["output_path"], "rio.v"), "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        hash_new = hash_md5.hexdigest()

        if hash_compiled != hash_new:
            riocore.log("!!! gateware changed: needs to be build and flash |||")
        elif hash_flashed != hash_new:
            riocore.log("!!! gateware changed: needs to flash |||")
        hash_file_new = os.path.join(cls.jdata["output_path"], "hash_new.txt")
        open(hash_file_new, "w").write(hash_new)


class component(cbase):
    filename_functions = "hal_functions.c"
    rtapi_mode = True
    typemap = {
        "float": "hal_float_t",
        "bool": "hal_bit_t",
        "s32": "hal_s32_t",
        "u32": "hal_u32_t",
    }
    printf = "rtapi_print"
    header_list = [
        "rtapi.h",
        "rtapi_app.h",
        "hal.h",
        "unistd.h",
        "stdlib.h",
        "stdbool.h",
        "stdio.h",
        "string.h",
        "math.h",
        "sys/mman.h",
        "errno.h",
    ]
    module_info = {
        "AUTHOR": "Oliver Dippel",
        "DESCRIPTION": "Driver for RIO FPGA boards",
        "LICENSE": "GPL v2",
    }

    def __init__(self, project):
        self.project = project
        self.base_path = os.path.join(self.project.config["output_path"], "LinuxCNC")
        self.component_path = f"{self.base_path}"
        os.makedirs(self.component_path, exist_ok=True)
        output = self.mainc(project)
        open(os.path.join(self.component_path, "riocomp.c"), "w").write("\n".join(output))

    def vinit(self, vname, vtype, halstr=None, vdir="input"):
        vtype = {"bool": "bit"}.get(vtype, vtype)
        direction = {"output": "IN", "input": "OUT", "inout": "IO"}.get(vdir, vdir)
        return f'    if (retval = hal_pin_{vtype}_newf(HAL_{direction}, &(data->{vname}), comp_id, "%s.{halstr}", prefix) != 0) error_handler(retval);'
