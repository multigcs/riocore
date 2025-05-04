import hashlib
import importlib
import os
import shutil
import stat
import json

riocore_path = os.path.dirname(os.path.dirname(__file__))


class Gateware:
    def __init__(self, project):
        self.project = project
        self.gateware_path = os.path.join(project.config["output_path"], "Gateware")
        project.config["riocore_path"] = riocore_path

    def globals(self):
        # create globals.v for compatibility functions
        globals_data = []
        globals_data.append(f'localparam FPGA_FAMILY = "{self.config.get("family", "UNKNOWN")}";')
        globals_data.append(f'localparam FPGA_TYPE = "{self.config.get("type", "UNKNOWN")}";')
        globals_data.append(f'localparam TOOLCHAIN = "{self.toolchain}";')
        globals_data.append("")
        if self.config.get("family", "UNKNOWN") in {"ice40"}:
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
        open(os.path.join(self.gateware_path, "globals.v"), "w").write("\n".join(globals_data))
        self.verilogs.append("globals.v")

    def generator(self, generate_pll=True):
        self.config = self.project.config.copy()

        os.makedirs(self.gateware_path, exist_ok=True)

        toolchains_json_path = os.path.join(riocore_path, "toolchains.json")
        if os.path.isfile(toolchains_json_path):
            self.config["toolchains_json"] = json.loads(open(toolchains_json_path, "r").read())
            if self.config["toolchains_json"]:
                for toolchain, path in self.config["toolchains_json"].items():
                    if path and not os.path.isdir(path):
                        print(f"WARNING: toolchains.json: path for '{toolchain}' not found: {path}")
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

        self.generate_pll = generate_pll
        self.toolchain = self.project.config["toolchain"]
        print(f"loading toolchain {self.toolchain}")
        self.toolchain_generator = importlib.import_module(".toolchain", f"riocore.generator.toolchains.{self.toolchain}").Toolchain(self.config)
        self.expansion_pins = []
        for plugin_instance in self.project.plugin_instances:
            for pin in plugin_instance.expansion_outputs():
                self.expansion_pins.append(pin)
            for pin in plugin_instance.expansion_inputs():
                self.expansion_pins.append(pin)

        self.virtual_pins = []
        for plugin_instance in self.project.plugin_instances:
            for pin_name, pin_config in plugin_instance.pins().items():
                if "pin" in pin_config and pin_config["pin"].startswith("VIRT:"):
                    pinname = pin_config["pin"]
                    if pinname not in self.virtual_pins:
                        self.virtual_pins.append(pinname)

        self.verilogs = []
        self.linked_pins = []
        self.globals()
        self.top()
        self.makefile()
        self.interface_html()

    def interface_html(self):
        output = []
        output.append("<h1>Interface</h1>")
        output.append("<table width='100%'>")
        output.append("<tr><td valign='top'>")
        output.append("<h3>FPGA to Host</h3>")
        output.append("<table width='100%'>")
        for data in self.iface_in:
            name = data[0]
            output.append(
                f"<tr><td style='padding: 3px; border: 1px solid black;'>{data[1]}{'bits' if data[1] > 1 else 'bit'}</td><td  style='padding: 3px; border: 1px solid black;' align='center'>{name}</td></tr>"
            )
        output.append("</table>")
        output.append("</td><td valign='top'>")
        output.append("<h3>Host to FPGA</h3>")
        output.append("<table width='100%'>")
        for data in self.iface_out:
            name = data[0]
            output.append(
                f"<tr><td style='padding: 3px; border: 1px solid black;'>{data[1]}{'bits' if data[1] > 1 else 'bit'}</td><td  style='padding: 3px; border: 1px solid black;' align='center'>{name}</td></tr>"
            )
        output.append("</table>")
        output.append("</td></tr>")
        output.append("</table>")

        open(os.path.join(self.gateware_path, "interface.html"), "w").write("\n".join(output))

    def makefile(self):
        flashcmd = self.config.get("flashcmd")
        if flashcmd:
            if flashcmd.startswith("./") and self.project.config["json_path"]:
                flashcmd_script = flashcmd.split()[0].replace("./", "")
                json_path = self.project.config["json_path"]
                flashcmd_script_path = os.path.join(json_path, flashcmd_script)
                print(flashcmd_script_path)
                if os.path.isfile(flashcmd_script_path):
                    target = os.path.join(self.gateware_path, flashcmd_script)
                    shutil.copy(flashcmd_script_path, target)
                    os.chmod(target, stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR | stat.S_IRGRP | stat.S_IXGRP | stat.S_IROTH | stat.S_IXOTH)

        for plugin_instance in self.project.plugin_instances:
            for verilog in plugin_instance.gateware_files():
                if verilog in self.verilogs:
                    continue
                self.verilogs.append(verilog)
                ipv_path = os.path.join(riocore_path, "plugins", plugin_instance.NAME, verilog)
                target = os.path.join(self.gateware_path, verilog)
                shutil.copy(ipv_path, target)

            for verilog, data in plugin_instance.gateware_virtual_files().items():
                if verilog in self.verilogs:
                    continue
                self.verilogs.append(verilog)
                target = os.path.join(self.gateware_path, verilog)
                open(target, "w").write(data)

        for extrafile in ("debouncer.v", "toggle.v", "pwmmod.v", "oneshot.v"):
            self.verilogs.append(extrafile)
            source = os.path.join(riocore_path, "files", extrafile)
            target = os.path.join(self.gateware_path, extrafile)
            shutil.copy(source, target)
        self.verilogs.append("rio.v")
        self.config["verilog_files"] = self.verilogs
        self.config["pinlists"] = {}
        self.config["pinlists"]["base"] = {}
        self.config["pinlists"]["base"]["sysclk_in"] = {"direction": "input", "pull": None, "pin": self.config["sysclk_pin"], "varname": "sysclk_in"}

        self.config["timing_constraints"] = {}
        self.config["timing_constraints_instance"] = {}
        for plugin_instance in self.project.plugin_instances:
            for key, value in plugin_instance.timing_constraints().items():
                if ":" in key:
                    pre, post = key.split(":")
                    pname = f"{pre}_{plugin_instance.instances_name}_{post}".upper()
                    self.config["timing_constraints"][pname] = value
                else:
                    self.config["timing_constraints_instance"][f"{plugin_instance.instances_name}.{key}"] = value

        self.pinmapping = {}
        self.pinmapping_rev = {}
        self.slots = self.config["board_data"].get("slots", []) + self.config["jdata"].get("slots", [])
        for slot in self.slots:
            slot_name = slot.get("name")
            slot_pins = slot.get("pins", {})
            for pin_name, pin in slot_pins.items():
                if isinstance(pin, dict):
                    pin = pin["pin"]
                pin_id = f"{slot_name}:{pin_name}"
                self.pinmapping[pin_id] = pin
                self.pinmapping_rev[pin] = pin_id

        pinnames = {}
        for plugin_instance in self.project.plugin_instances:
            self.config["pinlists"][plugin_instance.instances_name] = {}
            for pin_name, pin_config in plugin_instance.pins().items():
                if "pin" in pin_config and pin_config["pin"] not in self.expansion_pins and pin_config["pin"] not in self.virtual_pins and pin_config["varname"] not in self.linked_pins:
                    pin_config["pin"] = self.pinmapping.get(pin_config["pin"], pin_config["pin"])
                    self.config["pinlists"][plugin_instance.instances_name][pin_name] = pin_config
                    if pin_config["pin"] not in pinnames:
                        pinnames[pin_config["pin"]] = plugin_instance.instances_name
                    else:
                        print(f"ERROR: pin allready exist {pin_config['pin']} ({plugin_instance.instances_name} / {pinnames[pin_config['pin']]})")

        self.toolchain_generator.generate(self.gateware_path)

    def top(self):
        output = []
        input_variables_list = ["header_tx[7:0], header_tx[15:8], header_tx[23:16], header_tx[31:24]"]
        input_variables_list += ["timestamp[7:0], timestamp[15:8], timestamp[23:16], timestamp[31:24]"]
        output_variables_list = []
        self.iface_in = []
        self.iface_out = []
        output_pos = self.project.buffer_size

        variable_name = "header_rx"
        size = 32
        pack_list = []
        for bit_num in range(0, size, 8):
            pack_list.append(f"rx_data[{output_pos - 1}:{output_pos - 8}]")
            output_pos -= 8
        output_variables_list.append(f"// PC -> FPGA ({self.project.output_size} + FILL)")
        output_variables_list.append(f"// assign {variable_name} = {{{', '.join(reversed(pack_list))}}};")
        self.iface_out.append(["RX_HEADER", size])
        self.iface_in.append(["TX_HEADER", size])
        self.iface_in.append(["TITMESTAMP", size])

        if self.project.multiplexed_input:
            variable_name = "MULTIPLEXED_INPUT_VALUE"
            size = self.project.multiplexed_input_size
            pack_list = []
            for bit_num in range(0, size, 8):
                pack_list.append(f"{variable_name}[{bit_num + 7}:{bit_num}]")
            input_variables_list.append(f"{', '.join(pack_list)}")
            self.iface_in.append([variable_name, size])
            variable_name = "MULTIPLEXED_INPUT_ID"
            size = 8
            pack_list = []
            for bit_num in range(0, size, 8):
                pack_list.append(f"{variable_name}[{bit_num + 7}:{bit_num}]")
            input_variables_list.append(f"{', '.join(pack_list)}")
            self.iface_in.append([variable_name, size])

        if self.project.multiplexed_output:
            variable_name = "MULTIPLEXED_OUTPUT_VALUE"
            size = self.project.multiplexed_output_size
            pack_list = []
            for bit_num in range(0, size, 8):
                pack_list.append(f"rx_data[{output_pos - 1}:{output_pos - 8}]")
                output_pos -= 8
            output_variables_list.append(f"assign {variable_name} = {{{', '.join(reversed(pack_list))}}};")
            self.iface_out.append([variable_name, size])
            variable_name = "MULTIPLEXED_OUTPUT_ID"
            size = 8
            pack_list = []
            for bit_num in range(0, size, 8):
                pack_list.append(f"rx_data[{output_pos - 1}:{output_pos - 8}]")
                output_pos -= 8
            output_variables_list.append(f"assign {variable_name} = {{{', '.join(reversed(pack_list))}}};")
            self.iface_out.append([variable_name, size])

        for size, plugin_instance, data_name, data_config in self.project.get_interface_data():
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
                    self.iface_in.append([variable_name, size])
            elif data_config["direction"] == "output":
                if not data_config.get("expansion"):
                    pack_list = []
                    if size >= 8:
                        for bit_num in range(0, size, 8):
                            pack_list.append(f"rx_data[{output_pos - 1}:{output_pos - 8}]")
                            output_pos -= 8
                    else:
                        pack_list.append(f"rx_data[{output_pos - 1}]")
                        output_pos -= 1
                    output_variables_list.append(f"assign {variable_name} = {{{', '.join(reversed(pack_list))}}};")
                    self.iface_out.append([variable_name, size])

        if self.project.buffer_size > self.project.input_size:
            diff = self.project.buffer_size - self.project.input_size
            input_variables_list.append(f"{diff}'d0")

        diff = self.project.buffer_size - self.project.output_size
        if self.project.buffer_size > self.project.output_size:
            output_variables_list.append(f"// assign FILL = rx_data[{diff - 1}:0];")

        if output_pos != diff:
            print("ERROR: wrong buffer sizes")
            exit(1)

        arguments_list = ["input sysclk_in"]
        existing_pins = {}
        double_pins = {}
        for plugin_instance in self.project.plugin_instances:
            for pin_name, pin_config in plugin_instance.pins().items():
                if "pin" in pin_config and pin_config["pin"] not in self.expansion_pins and pin_config["pin"] not in self.virtual_pins:
                    if pin_config["pin"] in existing_pins:
                        double_pins[pin_config["pin"]] = pin_config["varname"]

                    else:
                        arguments_list.append(f"{pin_config['direction'].lower()} {pin_config['varname']}")
                        existing_pins[pin_config["pin"]] = pin_config["varname"]

        output.append("/*")
        output.append(f"    ######### {self.project.config['name']} #########")
        output.append("")
        output.append("")
        for key in ("toolchain", "family", "type", "package"):
            value = self.project.config[key]
            output.append(f"    {key.title():10}: {value}")
        output.append(f"    Clock     : {(self.project.config['speed'] / 1000000)} Mhz")
        output.append("")
        for plugin_instance in self.project.plugin_instances:
            for pin_name, pin_config in plugin_instance.pins().items():
                if "pin" in pin_config and pin_config["pin"] not in self.expansion_pins:
                    pull = "PULL{pin_config.get('pull').upper()}" if pin_config.get("pull") else ""
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
        arguments_string = ",\n        ".join(arguments_list)
        output.append(f"        {arguments_string}")
        output.append("    );")
        output.append("")
        output.append(f"    parameter BUFFER_SIZE = 16'd{self.project.buffer_size}; // {self.project.buffer_size // 8} bytes")
        output.append("")
        output.append("    reg INTERFACE_TIMEOUT = 0;")

        output.append("    wire INTERFACE_SYNC;")
        error_signals = ["INTERFACE_TIMEOUT"]

        estop_pin = None
        for plugin_instance in self.project.plugin_instances:
            for data_name, interface_setup in plugin_instance.interface_data().items():
                if plugin_instance.plugin_setup.get("is_joint", False) is False:
                    if plugin_instance.NAME == "bitin" and plugin_instance.title.lower() == "estop":
                        estop_pin = interface_setup["variable"]
                        break

                error_on = interface_setup.get("error_on")
                if error_on is True:
                    error_signals.append(interface_setup["variable"])
                elif error_on is False:
                    error_signals.append(f"~{interface_setup['variable']}")

        if estop_pin is not None:
            output.append("    wire ESTOP;")
            output.append(f"    assign ESTOP = {estop_pin};")
            error_signals.append("ESTOP")
        else:
            output.append("    parameter ESTOP = 0;")
        output.append("    wire ERROR;")

        output.append(f"    assign ERROR = ({' | '.join(error_signals)});")

        output.append("")

        osc_clock = self.project.config["osc_clock"]
        if osc_clock:
            speed = self.project.config["speed"]
            if self.generate_pll:
                if hasattr(self.toolchain_generator, "pll"):
                    self.toolchain_generator.pll(float(osc_clock), float(speed))
                else:
                    print(f"WARNING: can not generate pll for this platform: set speed to: {speed} Hz")
                    self.config["speed"] = speed
            else:
                print("INFO: preview-mode / no pll generated")

            if self.project.config["jdata"]["family"] == "Trion":
                output.append("    wire sysclk;")
                output.append("    assign sysclk = sysclk_in;")
            else:
                self.verilogs.append("pll.v")
                output.append("    wire sysclk;")
                output.append("    wire locked;")
                if self.project.config["jdata"]["family"] == "MAX 10":
                    output.append("    pll mypll(.inclk0(sysclk_in), .c0(sysclk), .locked(locked));")
                elif self.project.config["jdata"]["family"] == "xc7":
                    output.append("    wire sysclk25;")
                    output.append("    wire reset;")
                    output.append("    pll mypll(.clock_in(sysclk_in), .clock_out(sysclk), .clock25_out(sysclk25), .locked(locked), .reset(reset));")
                else:
                    output.append("    pll mypll(sysclk_in, sysclk, locked);")
        else:
            output.append("    wire sysclk;")
            output.append("    assign sysclk = sysclk_in;")
        output.append("")

        sysclk_speed = self.project.config["speed"]
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

        output.append(f"    wire[{self.project.buffer_size - 1}:0] rx_data;")
        output.append(f"    wire[{self.project.buffer_size - 1}:0] tx_data;")
        output.append("")
        output.append("    reg [31:0] timestamp = 0;")
        output.append("    reg signed [31:0] header_tx = 0;")
        output.append("    always @(posedge sysclk) begin")
        output.append("        timestamp <= timestamp + 1'd1;")
        output.append("        if (ESTOP) begin")
        output.append("            header_tx <= 32'h65737470;")
        output.append("        end else begin")
        output.append("            header_tx <= 32'h64617461;")
        output.append("        end")
        output.append("    end")
        output.append("")

        if double_pins:
            output.append("// linking double used input pins")
            for pin, varname in double_pins.items():
                if varname.startswith("PININ_"):
                    output.append(f"    wire {varname};")
                    output.append(f"    assign {varname} = {existing_pins[pin]};")
                    self.linked_pins.append(varname)
                else:
                    print(f"ERROR: can not assign output pin to multiple plugins: {varname} / {existing_pins[pin]} -> {pin}")

        # virtual pins
        for pin in self.virtual_pins:
            pinname = pin.replace(":", "_")
            output.append(f"    wire {pinname};")

        for plugin_instance in self.project.plugin_instances:
            for pin_name, pin_config in plugin_instance.pins().items():
                if "pin" in pin_config and pin_config["pin"] in self.virtual_pins:
                    pinname = pin_config["pin"].replace(":", "_")
                    if pin_config["direction"] == "output":
                        output.append(f"    wire {pin_config['varname']};")
                        output.append(f"    assign {pinname} = {pin_config['varname']}; // {pin_config['direction']}")
                    elif pin_config["direction"] == "input":
                        output.append(f"    wire {pin_config['varname']};")
                        output.append(f"    assign {pin_config['varname']} = {pinname}; // {pin_config['direction']}")

        # multiplexing
        if self.project.multiplexed_input:
            output.append(f"    reg [{self.project.multiplexed_input_size - 1}:0] MULTIPLEXED_INPUT_VALUE;")
            output.append("    reg [7:0] MULTIPLEXED_INPUT_ID;")
        if self.project.multiplexed_output:
            output.append(f"    wire [{self.project.multiplexed_output_size - 1}:0] MULTIPLEXED_OUTPUT_VALUE;")
            output.append("    wire [7:0] MULTIPLEXED_OUTPUT_ID;")

        for plugin_instance in self.project.plugin_instances:
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
        output.append(f"    // FPGA -> PC ({self.project.input_size} + FILL)")
        output.append("    assign tx_data = {")
        input_variables_string = ",\n        ".join(input_variables_list)
        output.append(f"        {input_variables_string}")
        output.append("    };")
        output.append("")

        # gateware_defines
        for plugin_instance in self.project.plugin_instances:
            define_string = "\n    ".join(plugin_instance.gateware_defines())
            if define_string:
                output.append(f"    {define_string}")
        output.append("")

        # expansion assignments
        used_expansion_outputs = []
        for plugin_instance in self.project.plugin_instances:
            for pin_name, pin_config in plugin_instance.pins().items():
                if "pin" in pin_config:
                    if pin_config["pin"] in self.expansion_pins:
                        output.append(f"    wire {pin_config['varname']};")

        for plugin_instance in self.project.plugin_instances:
            for pin_name, pin_config in plugin_instance.pins().items():
                if "pin" in pin_config:
                    if pin_config["pin"] in self.expansion_pins:
                        if pin_config["direction"] == "input":
                            output.append(f"    assign {pin_config['varname']} = {pin_config['pin']};")
                        elif pin_config["direction"] == "output":
                            used_expansion_outputs.append(pin_config["pin"])

        output.append("    // update expansion output pins")
        output.append("    always @(posedge sysclk) begin")
        # update expansion output pins
        for plugin_instance in self.project.plugin_instances:
            for pin_name, pin_config in plugin_instance.pins().items():
                if "pin" in pin_config:
                    if pin_config["pin"] in self.expansion_pins:
                        if pin_config["direction"] == "output":
                            output.append(f"        {pin_config['pin']} <= {pin_config['varname']};")
        # set expansion output pins without driver
        for plugin_instance in self.project.plugin_instances:
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
                                output.append(f"        {variable} <= {size}'d{default};")
                        else:
                            for bit_num in range(0, size):
                                bitvar = f"{variable}[{bit_num}]"
                                if bitvar not in used_expansion_outputs:
                                    if default & (1 << bit_n):
                                        output.append(f"        {bitvar} <= 1'd1;")
                                    else:
                                        output.append(f"        {bitvar} <= 1'd0;")
        output.append("    end")

        if self.project.multiplexed_input:
            output.append("    always @(posedge sysclk) begin")
            output.append("        if (INTERFACE_SYNC_RISINGEDGE == 1) begin")
            output.append(f"            if (MULTIPLEXED_INPUT_ID < {self.project.multiplexed_input - 1}) begin")
            output.append("                MULTIPLEXED_INPUT_ID = MULTIPLEXED_INPUT_ID + 1'd1;")
            output.append("            end else begin")
            output.append("                MULTIPLEXED_INPUT_ID = 0;")
            output.append("            end")
            mpid = 0
            for size, plugin_instance, data_name, data_config in self.project.get_interface_data():
                multiplexed = data_config.get("multiplexed", False)
                if not multiplexed:
                    continue
                variable_name = data_config["variable"]
                direction = data_config["direction"]
                if direction == "input":
                    output.append(f"            if (MULTIPLEXED_INPUT_ID == {mpid}) begin")
                    if size == 1:
                        output.append(f"                MULTIPLEXED_INPUT_VALUE = {variable_name};")
                    else:
                        output.append(f"                MULTIPLEXED_INPUT_VALUE = {variable_name}[{size - 1}:0];")
                    output.append("            end")
                    mpid += 1
            output.append("        end")
            output.append("    end")

        if self.project.multiplexed_output:
            output.append("    always @(posedge sysclk) begin")
            mpid = 0
            for size, plugin_instance, data_name, data_config in self.project.get_interface_data():
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

        # gateware instances
        for plugin_instance in self.project.plugin_instances:
            if not plugin_instance.gateware_instances():
                continue
            output.append("")
            output.append(f"    // Name: {plugin_instance.plugin_setup.get('name', plugin_instance.instances_name)} ({plugin_instance.NAME})")
            for instance_name, instance_config in plugin_instance.gateware_instances().items():
                instance_module = instance_config.get("module")
                instance_parameter = instance_config.get("parameter")
                instance_arguments = instance_config.get("arguments")
                instance_predefines = instance_config.get("predefines")
                instance_direct = instance_config.get("direct")
                if instance_predefines:
                    predefines = "\n    ".join(instance_predefines)
                    output.append(f"    {predefines}")
                if not instance_direct:
                    if instance_arguments:
                        if instance_parameter:
                            output.append(f"    {instance_module} #(")
                            parameters_list = []
                            for parameter_name, parameter_value in instance_parameter.items():
                                parameters_list.append(f".{parameter_name}({parameter_value})")
                            parameters_string = ",\n        ".join(parameters_list)
                            output.append(f"        {parameters_string}")
                            output.append(f"    ) {instance_name} (")
                        else:
                            output.append(f"    {instance_module} {instance_name} (")
                        arguments_list = []
                        for argument_name, argument_value in instance_arguments.items():
                            arguments_list.append(f".{argument_name}({argument_value})")
                        arguments_string = ",\n        ".join(arguments_list)
                        output.append(f"        {arguments_string}")
                        output.append("    );")
        output.append("")
        output.append("endmodule")
        output.append("")
        print(f"writing gateware to: {self.gateware_path}")
        open(os.path.join(self.gateware_path, "rio.v"), "w").write("\n".join(output))

        # write hash of rio.v to filesystem
        hash_file_compiled = os.path.join(self.gateware_path, "hash_compiled.txt")
        hash_compiled = ""
        if os.path.isfile(hash_file_compiled):
            hash_compiled = open(hash_file_compiled, "r").read()

        hash_file_flashed = os.path.join(self.gateware_path, "hash_flashed.txt")
        hash_flashed = ""
        if os.path.isfile(hash_file_flashed):
            hash_flashed = open(hash_file_flashed, "r").read()

        hash_md5 = hashlib.md5()
        with open(os.path.join(self.gateware_path, "rio.v"), "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        hash_new = hash_md5.hexdigest()

        if hash_compiled != hash_new:
            print("!!! gateware changed: needs to be build and flash |||")
        elif hash_flashed != hash_new:
            print("!!! gateware changed: needs to flash |||")
        hash_file_new = os.path.join(self.gateware_path, "hash_new.txt")
        open(hash_file_new, "w").write(hash_new)
